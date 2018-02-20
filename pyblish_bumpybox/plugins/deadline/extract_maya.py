from pyblish import api
from pyblish_bumpybox import inventory


class ExtractMaya(api.InstancePlugin):
    """ Appending Deadline data to deadline instances. """

    families = ["deadline"]
    order = inventory.get_order(__file__, "ExtractMaya")
    label = "Deadline"
    hosts = ["maya"]
    targets = ["process.deadline"]

    def process(self, instance):
        import math
        import os

        import pymel.core
        from pymel import versions

        collection = instance.data["collection"]

        # Getting job data.
        job_data = {
            "Plugin": "MayaBatch",
            "OutputFilename0": collection.format(
                "{head}" + "#" * collection.padding + "{tail}"
            ),
            "Priority": instance.data["deadlinePriority"],
            "Pool": instance.data["deadlinePool"],
            "ConcurrentTasks": instance.data["deadlineConcurrentTasks"]
        }

        # Frame range
        render_globals = pymel.core.PyNode("defaultRenderGlobals")
        start_frame = int(render_globals.startFrame.get())
        end_frame = int(render_globals.endFrame.get())
        step_frame = int(render_globals.byFrameStep.get())

        job_data["Frames"] = "{0}-{1}x{2}".format(
            start_frame, end_frame, step_frame
        )

        # Chunk size
        job_data["ChunkSize"] = instance.data["deadlineChunkSize"]
        if len(list(collection)) == 1:
            job_data["ChunkSize"] = str(end_frame)
        else:
            tasks = (end_frame - start_frame + 1.0) / step_frame
            chunks = (end_frame - start_frame + 1.0) / job_data["ChunkSize"]
            # Deadline can only handle 5000 tasks maximum
            if tasks > 5000 and chunks > 5000:
                job_data["ChunkSize"] = str(int(math.ceil(tasks / 5000.0)))

        # Setting plugin data
        plugin_data = {
            "Renderer": "file",
            "UseLegacyRenderLayers": 0,
            "UsingRenderLayers": 1,
            "RenderLayer": instance[0].name(),
            "Version": versions.flavor(),
            "MaxProcessors": 0,
            "LocalRendering": 1,
            "SceneFile": instance.context.data["currentFile"],
            "ProjectPath": os.path.dirname(
                instance.context.data["currentFile"]
            ),
            "OutputFilePath": os.path.join(
                os.path.dirname(instance.context.data["currentFile"]),
                "workspace"
            )
        }

        # Arnold plugin settings
        if "arnold" in instance.data.get("families", []):
            plugin_data["Renderer"] = "arnold"
            plugin_data["ArnoldVerbose"] = 1
            plugin_data["Animation"] = 1

        # Setting data
        data = instance.data.get(
            "deadlineData", {"job": {}, "plugin": {}}
        )

        for key, value in job_data.iteritems():
            if key not in data["job"].keys():
                data["job"][key] = value

        for key, value in plugin_data.iteritems():
            if key not in data["plugin"].keys():
                data["plugin"][key] = value

        instance.data["deadlineData"] = data
