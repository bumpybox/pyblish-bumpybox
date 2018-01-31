from pyblish import api
from pyblish_bumpybox import inventory


class CollectNukeStudioProjectData(api.ContextPlugin):
    """Collect the Ftrack project data.

    Offset to get collected Ftrack data from pyblish-ftrack.

    Its assumed at tag is applied to the active sequence with these keys:

    name - The project"s code.
    full_name - The project"s full name.
    project_schema_id - The id of the workflow schema applied to the project.

    Optional keys:

    root - The project"s root.
    disk_id - The id of the disk applied to the project.
    """

    order = inventory.get_order(__file__, "CollectNukeStudioProjectData")
    label = "Ftrack Project Data"
    hosts = ["nukestudio"]

    def process(self, context):
        from pyblish_bumpybox.utils import Window

        data = {
            "name": "",
            "full_name": "",
            "project_schema_id": "",
            "root": "",
            "disk_id": ""
        }

        # Get project data from launched task.
        task = context.data["ftrackTask"]
        if task:
            project = task["project"]
            data.update(
                {
                    "name": project["name"],
                    "full_name": project["full_name"],
                    "project_schema_id": project["project_schema_id"],
                    "root": project["root"],
                    "disk_id": project["disk_id"]
                }
            )

        # Get data from active sequence tag.
        data.update(self.get_sequence_data(context))

        # Show project input dialog if any data is missing.
        show_gui = False
        for key, value in data.iteritems():
            if key not in ["name", "full_name", "project_schema_id"]:
                continue

            if not value:
                show_gui = True

        if show_gui:
            win = Window(data=data)
            win.exec_()
            self.log.info(
                "Creating tag on sequence with data: {0}".format(win.data)
            )

        # Persist data
        self.log.info("Found project data: {0}".format(data))
        context.data["ftrackProjectData"] = data

    def get_sequence_data(self, context):
        import hiero

        data = {
            "name": "",
            "full_name": "",
            "project_schema_id": "",
            "root": "",
            "disk_id": ""
        }

        # Get project name from existing tag
        for tag in hiero.ui.activeSequence().tags():
            if ("tag.ftrack") not in tag.metadata().keys():
                continue

            for key in data:
                if ("tag." + key) in tag.metadata().keys():
                    data[key] = tag.metadata().value(key)

        # Remove any empty key/value pairs.
        results = {}
        for key, value in data.iteritems():
            if value:
                results[key] = value

        return results


class CollectNukeStudioEntities(api.ContextPlugin):
    """Collect the Ftrack project data.

    Offset to get collected "trackItem" instances.
    """

    order = inventory.get_order(__file__, "CollectNukeStudioEntities")
    label = "Ftrack Entities"
    hosts = ["nukestudio"]

    def get_instance(self, instances, label, family):
        for instance in instances:
            if (instance.data["label"] == label and
               instance.data["family"] == family):
                return instance
        return None

    def process(self, context):

        instances = []
        for parent in context:
            if "trackItem" != parent.data["family"]:
                continue

            item = parent.data["item"]
            split = item.name().split("--")

            shot = None
            parent_instance = parent
            if "--" in item.name():
                # Get/Create sequence
                if len(split) == 2:
                    name = split[0]
                    family = "trackItem.ftrackEntity.sequence"
                    sequence = self.get_instance(instances, name, family)
                    if sequence is None:
                        sequence = context.create_instance(
                            name=name,
                            label=name,
                            parent=parent,
                            family=family,
                            families=["trackItem", "ftrackEntity", "sequence"]
                        )
                        instances.append(sequence)

                    parent_instance = sequence

                # Get/Create episode and sequence
                if len(split) == 3:
                    name = split[0]
                    family = "trackItem.ftrackEntity.episode"
                    episode = self.get_instance(instances, name, family)
                    if episode is None:
                        episode = context.create_instance(
                            name=name,
                            label=name,
                            parent=parent,
                            family=family,
                            families=["trackItem", "ftrackEntity", "episode"]
                        )
                        instances.append(episode)

                    label = "/".join([split[0], split[1]])
                    family = "trackItem.ftrackEntity.episode"
                    sequence = self.get_instance(instances, label, family)
                    if sequence is None:
                        sequence = context.create_instance(
                            name=split[1],
                            parent=episode,
                            label=label,
                            family="trackItem.ftrackEntity.sequence",
                            families=["trackItem", "ftrackEntity", "sequence"]
                        )
                        instances.append(sequence)

                    parent_instance = sequence

            # Create Ftrack shot instance
            label = "/".join(split)
            family = "trackItem.ftrackEntity.shot"
            shot = self.get_instance(instances, label, family)
            if shot is None:
                shot = context.create_instance(name=split[-1])
                shot.data["label"] = "/".join(split)
                shot.data["family"] = "trackItem.ftrackEntity.shot"
                shot.data["families"] = ["trackItem", "ftrackEntity", "shot"]
                shot.data["parent"] = parent_instance
                parent.data["shotInstance"] = shot
                shot.data["item"] = parent.data["item"]

                shot.data["handles"] = parent.data["handles"]
                shot.data["fstart"] = parent.data["startFrame"]
                shot.data["fend"] = parent.data["endFrame"]

                sequence = parent.data["item"].parent().parent()
                shot.data["fps"] = sequence.framerate().toFloat()

                if parent.data["item"].reformatState().type() == "disabled":
                    media_source = parent.data["item"].source().mediaSource()
                    shot.data["width"] = media_source.width()
                    shot.data["height"] = media_source.height()
                else:
                    shot.data["width"] = sequence.format().width()
                    shot.data["height"] = sequence.format().height()

                instances.append(shot)

            # Create Ftrack task instances.
            for tag in parent.data["item"].tags():
                if ("tag.ftrack") not in tag.metadata().keys():
                    continue

                metadata = tag.metadata().dict()

                if "tag.type" in metadata.keys():
                    # Expect "task_name" instead of "name", because "name"
                    # can't be edited by the user.
                    name = metadata.get(
                        "tag.task_name", metadata["tag.type"].lower()
                    )
                    task = context.create_instance(name=name)
                    label = shot.data["label"] + "/" + name
                    task.data["label"] = label
                    task.data["type"] = metadata["tag.type"]
                    task.data["family"] = "trackItem.ftrackEntity.task"
                    task.data["families"] = [
                        "trackItem", "ftrackEntity", "task"
                    ]
                    task.data["parent"] = shot

                if metadata["tag.ftrack"] == "assetbuild":
                    assetbuild = context.create_instance(name=tag.name())
                    label = shot.data["label"] + "/" + tag.name()
                    assetbuild.data["label"] = label
                    assetbuild.data["family"] = (
                        "trackItem.ftrackEntity.assetbuild"
                    )
                    assetbuild.data["families"] = [
                        "trackItem", "ftrackEntity", "assetbuild"
                    ]
                    assetbuild.data["shot"] = shot
                    assetbuild.data["id"] = metadata["tag.id"]
