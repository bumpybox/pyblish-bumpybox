import math

import pymel.core
from pymel import versions

import pyblish.api


class BumpyboxDeadlineExtractMaya(pyblish.api.InstancePlugin):
    """ Appending Deadline data to deadline instances. """

    families = ["deadline"]
    order = pyblish.api.ExtractorOrder
    label = "Deadline"
    hosts = ["maya"]

    def process(self, instance):

        collection = instance.data["collection"]

        job_data = {}
        plugin_data = {}
        if "deadlineData" in instance.data:
            job_data = instance.data["deadlineData"]["job"].copy()
            plugin_data = instance.data["deadlineData"]["plugin"].copy()

        # Setting job data.
        job_data["Plugin"] = "MayaBatch"

        # Replace houdini frame padding with Deadline padding
        fmt = "{head}" + "#" * collection.padding + "{tail}"
        job_data["OutputFilename0"] = collection.format(fmt)
        job_data["Priority"] = instance.data["deadlinePriority"]
        job_data["Pool"] = instance.data["deadlinePool"]
        job_data["ConcurrentTasks"] = instance.data["deadlineConcurrentTasks"]

        # Frame range
        render_globals = pymel.core.PyNode("defaultRenderGlobals")
        start_frame = int(render_globals.startFrame.get())
        end_frame = int(render_globals.endFrame.get())
        step_frame = int(render_globals.byFrameStep.get())

        job_data["Frames"] = "{0}-{1}x{2}".format(start_frame,
                                                  end_frame,
                                                  step_frame)

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
        plugin_data["SceneFile"] = instance.context.data["currentFile"]
        plugin_data["Version"] = versions.flavor()

        # Setting data
        data = {"job": job_data, "plugin": plugin_data}
        instance.data["deadlineData"] = data
