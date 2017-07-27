import pyblish.api


class ExtractFtrackProject(pyblish.api.ContextPlugin):
    """Extract an Ftrack project from context.data["ftrackProjectData"]"""

    order = pyblish.api.ExtractorOrder
    label = "Ftrack Project"
    hosts = ["nukestudio"]

    def process(self, context):

        session = context.data["ftrackSession"]

        data = {}
        for key, value in context.data["ftrackProjectData"].iteritems():
            if not value:
                continue

            data[key] = value

        # Get project from data
        query = "Project where "
        for key, value in data.iteritems():
            query += "{0} is \"{1}\" and ".format(key, value)
        query = query[:-5]

        project = session.query(query).first()

        # Create project if it does not exist
        if not project:
            self.log.info("Creating project with data: {0}".format(data))
            project = session.create("Project", data)
            session.commit()

        context.data["ftrackProject"] = project


class ExtractFtrackNukeStudioShot(pyblish.api.InstancePlugin):
    """Creates ftrack shots by the name of the shot."""

    order = ExtractFtrackProject.order + 0.01
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

        # Committing session so other instances can pick up on newly created
        # entities.
        self.session.commit()

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

            if "ftrackShot" not in instance.data.keys():
                continue

            shot = instance.data["ftrackShot"]

            for task_instance in task_instances:
                task = task_instance[0]
                if task in instance.data["tasks"]:
                    data = instance.data.get("asset_data", {})
                    data.update(
                        {
                            "name": task_instance.data["name"].split("--")[-1],
                            "parent": shot
                        }
                    )
                    instance.data["asset_data"] = data


class ExtractFtrackNukeStudioTasks(pyblish.api.InstancePlugin):
    """Creates ftrack tasks by tags."""

    order = ExtractFtrackNukeStudioShot.order + 0.01
    families = ["ftrack", "trackItem"]
    match = pyblish.api.Subset
    label = "Ftrack Tasks"
    optional = True
    hosts = ["nukestudio"]

    def process(self, instance):

        tasks_data = []
        for tag in instance[0].tags():
            if ("tag.ftrack") not in tag.metadata().keys():
                continue

            metadata = tag.metadata().dict()

            if "tag.type" in metadata.keys():
                tasks_data.append(
                    {
                        "type": metadata["tag.type"],
                        "name": metadata.get(
                            "tag.name", metadata["tag.type"].lower()
                        )
                    }
                )

        session = instance.context.data["ftrackSession"]
        shot = instance.data["ftrackShot"]
        tasks = []
        for data in tasks_data:
            task_type = session.query(
                'Type where name is "{0}"'.format(data["type"])
            ).one()

            query = (
                'Task where type.name is "{0}" and name is "{1}" and '
                'parent.id is "{2}"'
            )
            task = session.query(
                query.format(data["type"], data["name"], shot["id"])
            ).first()

            if not task:
                task = session.create(
                    "Task",
                    {"name": data["name"], "type": task_type, "parent": shot}
                )

            tasks.append(task)

        instance.data["ftrackTasks"] = tasks
