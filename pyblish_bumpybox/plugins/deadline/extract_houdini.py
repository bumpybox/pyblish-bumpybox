import math

import hou
import pyblish.api


class BumpyboxDeadlineExtractHoudini(pyblish.api.InstancePlugin):
    """ Appending Deadline data to deadline instances. """

    families = ["deadline"]
    order = pyblish.api.ExtractorOrder
    label = "Deadline"
    hosts = ["houdini"]

    def process(self, instance):

        node = instance[0]
        collection = instance.data["collection"]

        job_data = {}
        plugin_data = {}
        if "deadlineData" in instance.data:
            job_data = instance.data["deadlineData"]["job"].copy()
            plugin_data = instance.data["deadlineData"]["plugin"].copy()

        # Setting job data.
        job_data["Plugin"] = "Houdini"

        # Replace houdini frame padding with Deadline padding
        fmt = "{head}" + "#" * collection.padding + "{tail}"
        job_data["OutputFilename0"] = collection.format(fmt)
        job_data["Priority"] = instance.data["deadlinePriority"]
        job_data["Pool"] = instance.data["deadlinePool"]
        job_data["ConcurrentTasks"] = instance.data["deadlineConcurrentTasks"]

        # Frame range
        start_frame = int(node.parm("f1").eval())
        end_frame = int(node.parm("f2").eval())
        step_frame = int(node.parm("f3").eval())

        if node.parm("trange").eval() == 0:
            start_frame = end_frame = int(hou.frame())

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
        plugin_data["OutputDriver"] = node.path()
        plugin_data["Version"] = str(hou.applicationVersion()[0])
        plugin_data["IgnoreInputs"] = "0"
        plugin_data["SceneFile"] = instance.context.data["currentFile"]

        # Setting data
        data = {"job": job_data, "plugin": plugin_data}
        instance.data["deadlineData"] = data
