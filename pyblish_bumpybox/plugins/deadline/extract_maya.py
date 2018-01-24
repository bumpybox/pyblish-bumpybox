import pyblish.api


class ExtractMaya(pyblish.api.InstancePlugin):
    """ Appending Deadline data to deadline instances. """

    families = ["deadline"]
    order = pyblish.api.ExtractorOrder
    label = "Deadline"
    hosts = ["maya"]

    def process(self, instance):
        import math
        import os

        import pymel.core
        from pymel import versions

        collection = instance.data["collection"]

        data = instance.data.get(
            "deadlineData", {"job": {}, "plugin": {}}
        )

        # Setting job data.
        data["job"]["Plugin"] = "MayaBatch"

        # Replace houdini frame padding with Deadline padding
        fmt = "{head}" + "#" * collection.padding + "{tail}"
        data["job"]["OutputFilename0"] = collection.format(fmt)
        data["job"]["Priority"] = instance.data["deadlinePriority"]
        data["job"]["Pool"] = instance.data["deadlinePool"]
        value = instance.data["deadlineConcurrentTasks"]
        data["job"]["ConcurrentTasks"] = value

        # Frame range
        render_globals = pymel.core.PyNode("defaultRenderGlobals")
        start_frame = int(render_globals.startFrame.get())
        end_frame = int(render_globals.endFrame.get())
        step_frame = int(render_globals.byFrameStep.get())

        data["job"]["Frames"] = "{0}-{1}x{2}".format(
            start_frame, end_frame, step_frame
        )

        # Chunk size
        data["job"]["ChunkSize"] = instance.data["deadlineChunkSize"]
        if len(list(collection)) == 1:
            data["job"]["ChunkSize"] = str(end_frame)
        else:
            tasks = (end_frame - start_frame + 1.0) / step_frame
            chunks = (end_frame - start_frame + 1.0) / data["job"]["ChunkSize"]
            # Deadline can only handle 5000 tasks maximum
            if tasks > 5000 and chunks > 5000:
                data["job"]["ChunkSize"] = str(int(math.ceil(tasks / 5000.0)))

        # Setting plugin data
        data["plugin"]["Renderer"] = "file"
        data["plugin"]["UsingRenderLayers"] = 1
        data["plugin"]["RenderLayer"] = instance[0].name()
        data["plugin"]["Version"] = versions.flavor()
        data["plugin"]["UseLegacyRenderLayers"] = 1
        data["plugin"]["MaxProcessors"] = 0

        scene_file = instance.context.data["currentFile"]
        data["plugin"]["SceneFile"] = scene_file
        data["plugin"]["ProjectPath"] = os.path.dirname(scene_file)
        data["plugin"]["OutputFilePath"] = os.path.join(
            os.path.dirname(scene_file), "workspace"
        )

        # Arnold plugin settings
        if "arnold" in instance.data.get("families", []):
            data["plugin"]["Renderer"] = "arnold"
            data["plugin"]["ArnoldVerbose"] = 1
            data["plugin"]["Animation"] = 1

        # Setting data
        instance.data["deadlineData"] = data
