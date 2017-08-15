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


def ensure_entity(instance, entity_type):

    session = instance.context.data["ftrackSession"]

    parent_entity = instance.data["parent"].data.get("entity", None)
    if parent_entity is None:
        parent_entity = instance.context.data["ftrackProject"]

    # Query existence of entity
    entity = session.query(
        '{0} where parent.id is "{1}" and name is "{2}"'.format(
            entity_type,
            parent_entity["id"],
            instance.data["name"]
        )
    ).first()
    # Create entity if non-existent
    if not entity:
        entity = session.create(
            entity_type,
            {
                "parent": parent_entity,
                "name": instance.data["name"]
            }
        )

    return entity


class ExtractFtrackEpisode(pyblish.api.InstancePlugin):
    """Creates ftrack episodes by the name of the instance."""

    order = ExtractFtrackProject.order + 0.01
    families = ["ftrackEntity", "episode"]
    match = pyblish.api.Subset
    label = "Ftrack Episode"
    optional = True

    def process(self, instance):

        instance.data["entity"] = ensure_entity(instance, "Episode")
        instance.data["item"] = instance.data["parent"].data["item"]


class ExtractFtrackSequence(pyblish.api.InstancePlugin):
    """Creates ftrack sequences by the name of the instance."""

    order = ExtractFtrackEpisode.order + 0.01
    families = ["ftrackEntity", "sequence"]
    match = pyblish.api.Subset
    label = "Ftrack Sequence"
    optional = True

    def process(self, instance):

        instance.data["entity"] = ensure_entity(instance, "Sequence")
        instance.data["item"] = instance.data["parent"].data["item"]


class ExtractFtrackShot(pyblish.api.InstancePlugin):
    """Creates ftrack shots by the name of the instance."""

    order = ExtractFtrackSequence.order + 0.01
    families = ["ftrackEntity", "shot"]
    match = pyblish.api.Subset
    label = "Ftrack Shot"
    optional = True

    def process(self, instance):
        entity = ensure_entity(instance, "Shot")
        instance.data["entity"] = entity
        instance.data["item"] = instance.data["parent"].data["item"]

        # Assign attributes to shot
        attributes = {
            "handles": instance.data["handles"],
            "fstart": instance.data["fstart"],
            "fend": instance.data["fend"],
            "fps": instance.data["fps"],
            "width": instance.data["width"],
            "height": instance.data["height"],
        }

        for key, value in attributes.iteritems():
            try:
                entity["custom_attributes"][key] = value
            except Exception as e:
                self.log.warning("Could not set the attribute: " + str(e))


class ExtractFtrackThumbnail(pyblish.api.InstancePlugin):
    """Creates thumbnails from shots."""

    order = ExtractFtrackShot.order + 0.01
    families = ["ftrackEntity", "shot"]
    match = pyblish.api.Subset
    label = "Ftrack Thumbnail"
    optional = True

    def nukestudio(self, instance):
        import os
        import time
        import hiero

        item = instance.data["item"]

        nukeWriter = hiero.core.nuke.ScriptWriter()

        # Getting top most track with media.
        seq = item.parent().parent()
        item = seq.trackItemAt(item.timelineIn())

        root_node = hiero.core.nuke.RootNode(1, 1, fps=seq.framerate())
        nukeWriter.addNode(root_node)

        handles = instance.data["handles"]

        item.addToNukeScript(
            script=nukeWriter,
            firstFrame=1,
            includeRetimes=True,
            retimeMethod="Frame",
            startHandle=handles,
            endHandle=handles
        )

        input_path = item.source().mediaSource().fileinfos()[0].filename()
        filename = os.path.splitext(input_path)[0]
        filename += "_thumbnail.png"
        output_path = os.path.join(
            os.path.dirname(instance.context.data["currentFile"]),
            "workspace",
            os.path.basename(filename)
        )

        fmt = hiero.core.Format(300, 200, 1, "thumbnail")
        fmt.addToNukeScript(script=nukeWriter)

        write_node = hiero.core.nuke.WriteNode(output_path)
        write_node.setKnob("file_type", "png")
        nukeWriter.addNode(write_node)

        script_path = output_path.replace(".png", ".nk")
        nukeWriter.writeToDisk(script_path)
        logFileName = output_path.replace(".png", ".log")
        process = hiero.core.nuke.executeNukeScript(
            script_path,
            open(logFileName, "w")
        )

        while process.poll() is None:
            time.sleep(0.5)

        if os.path.exists(output_path):
            self.log.info("Thumbnail rendered successfully!")
            return output_path

        self.log.error("Thumbnail failed to render")
        return None

    def process(self, instance):
        import pyblish.api

        # Extract thumbnail
        methods = {"nukestudio": self.nukestudio}
        instance.data["entity"].create_thumbnail(
            methods[pyblish.api.current_host()](instance)
        )


class ExtractFtrackTasks(pyblish.api.InstancePlugin):
    """Creates ftrack shots by the name of the instance."""

    order = ExtractFtrackShot.order + 0.01
    families = ["ftrackEntity", "task"]
    match = pyblish.api.Subset
    label = "Ftrack Tasks"
    optional = True

    def process(self, instance):
        session = instance.context.data["ftrackSession"]

        task_type = session.query(
            'Type where name is "{0}"'.format(instance.data["type"])
        ).one()

        query = (
            'Task where type.name is "{0}" and name is "{1}" and '
            'parent.id is "{2}"'
        )
        task = session.query(
            query.format(
                instance.data["type"],
                instance.data["name"],
                instance.data["parent"].data["entity"]["id"]
            )
        ).first()

        if not task:
            task = session.create(
                "Task",
                {
                    "name": instance.data["name"],
                    "type": task_type,
                    "parent": instance.data["parent"].data["entity"]
                }
            )

        instance.data["entity"] = task


class ExtractFtrackCommit(pyblish.api.ContextPlugin):
    """Commits the Ftrack session for entities."""

    order = ExtractFtrackTasks.order + 0.01
    label = "Ftrack Commit"

    def process(self, context):

        context.data["ftrackSession"].commit()


class ExtractFtrackNukeStudio(pyblish.api.InstancePlugin):
    """Sets the Ftrack data for NukeStudio components."""

    order = ExtractFtrackTasks.order + 0.01
    label = "Ftrack NukeStudio"
    families = ["trackItem.task"]
    hosts = ["nukestudio"]

    def process(self, instance):
        # Asset data
        data = instance.data.get("asset_data", {})
        parent = instance.data["parent"]
        data["parent"] = parent.data["shotInstance"].data["entity"]
        instance.data["asset_data"] = data
