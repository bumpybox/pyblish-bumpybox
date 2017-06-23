import pyblish.api


class ExtractFtrackNukeStudioShot(pyblish.api.InstancePlugin):
    """Creates ftrack shots by the name of the shot.

    Offset to get extracted Ftrack project.
    """

    order = pyblish.api.ExtractorOrder + 0.1
    families = ["ftrack", "trackItem"]
    match = pyblish.api.Subset
    label = "Ftrack Shot"
    optional = True
    hosts = ["nukestudio"]

    def create_hierarchy(self, parent, data):

        query_template = '{0} where parent.id is "{1}" and name is "{2}"'

        if data["child"]:
            # Query existence of entity
            entity = self.session.query(
                query_template.format(data["type"], parent["id"], data["name"])
            ).first()

            # Create entity if non-existent
            if not entity:
                entity = self.session.create(
                    data["type"], {"parent": parent, "name": data["name"]}
                )

            # Return the leaf entity
            return self.create_hierarchy(entity, data["child"])
        else:
            # Query leaf entity
            entity = self.session.query(
                query_template.format(data["type"], parent["id"], data["name"])
            ).first()

            # Return existing or created entity
            if entity:
                return entity
            else:
                return self.session.create(
                    data["type"], {"parent": parent, "name": data["name"]}
                )

    def process(self, instance):

        item = instance[0]
        self.session = instance.context.data["ftrackSession"]

        # Get/Create shot
        parent = None
        task = instance.context.data["ftrackTask"]
        if task:
            parent = task["parent"]

        project = instance.context.data["ftrackProject"]
        if project:
            parent = project

        shot_data = {"name": item.name(), "child": None, "type": "Shot"}
        hierarchy_data = None
        if "--" in item.name():
            split = item.name().split("--")
            shot_data["name"] = split[-1]

            # Get/Create sequence
            if len(split) == 2:
                hierarchy_data = {
                    "name": split[0], "child": shot_data, "type": "Sequence"
                }

            # Get/Create episode and sequence
            if len(split) == 3:
                sequence_data = {
                    "name": split[1], "child": shot_data, "type": "Sequence"
                }
                hierarchy_data = {
                    "name": split[0], "child": sequence_data, "type": "Episode"
                }
        else:
            hierarchy_data = shot_data

        shot = self.create_hierarchy(parent, hierarchy_data)

        instance.data["ftrackShot"] = shot

        # Assign attributes to shot
        start_frame = 1
        handles = 0
        task = instance.data["tasks"][0]
        if task._startFrame:
            start_frame = task._startFrame
        if task._cutHandles:
            handles = task._cutHandles
        shot["custom_attributes"]["fstart"] = start_frame
        shot["custom_attributes"]["handles"] = handles

        duration = item.sourceOut() - item.sourceIn()
        duration = abs(int(round((abs(duration) + 1) / item.playbackSpeed())))
        end_frame = start_frame + duration
        shot["custom_attributes"]["fend"] = end_frame

        sequence = item.parent().parent()
        shot["custom_attributes"]["fps"] = sequence.framerate().toFloat()

        try:
            fmt = sequence.format()
            shot["custom_attributes"]["width"] = fmt.width()
            shot["custom_attributes"]["height"] = fmt.height()
        except Exception as e:
            self.log.warning("Could not set the resolution: " + str(e))


class ExtractFtrackNukeStudioTaskParent(pyblish.api.ContextPlugin):
    """Extract the task parent from the created Ftrack shots."""

    order = ExtractFtrackNukeStudioShot.order + 0.01
    label = "Ftrack Task Parent"
    hosts = ["nukestudio"]

    def process(self, context):

        task_instances = []
        for instance in context:
            families = instance.data.get("families", [])
            families.append(instance.data["family"])

            if "task" not in families:
                continue

            if "ftrack" not in families:
                continue

            task_instances.append(instance)

        for instance in context:
            families = instance.data.get("families", [])
            families.append(instance.data["family"])

            if "trackItem" not in families:
                continue

            if "ftrack" not in families:
                continue

            shot = instance.data["ftrackShot"]
            for task_instance in task_instances:
                task = task_instance[0]
                if task in instance.data["tasks"]:
                    task_instance.data["asset_parent"] = shot
                    name = task_instance.data["name"]
                    task_instance.data["asset_name"] = name.split("--")[-1]
