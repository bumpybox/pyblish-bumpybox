import hou

import pyblish.api


class AppendDeadlineDataFarm(pyblish.api.InstancePlugin):
    """ Appending Deadline data to farm related instances """

    families = ["img.farm.*", "cache.farm.*"]
    order = pyblish.api.ExtractorOrder

    def process(self, instance):

        node = instance[0]

        job_data = {}
        plugin_data = {}
        if "deadlineData" in instance.data:
            job_data = instance.data["deadlineData"]["job"].copy()
            plugin_data = instance.data["deadlineData"]["plugin"].copy()

        # setting job data
        job_data["Plugin"] = "Houdini"

        # replace houdini frame padding with deadline padding, and
        # add to job data
        path = instance.data["outputPath"]
        job_data["OutputFilename0"] = path.replace("$F4", "####")

        # frame range
        start_frame = int(node.parm("f1").eval())
        end_frame = int(node.parm("f2").eval())

        if node.parm("trange").eval() == 0:
            start_frame = end_frame = int(hou.frame())

        job_data["Frames"] = "{0}-{1}".format(start_frame, end_frame)

        # chunk size
        if "%" not in path:
            job_data["ChunkSize"] = str(end_frame)

        # setting plugin data
        plugin_data["OutputDriver"] = node.path()
        plugin_data["Version"] = str(hou.applicationVersion()[0])
        plugin_data["IgnoreInputs"] = "0"
        plugin_data["SceneFile"] = instance.context.data["currentFile"]

        # setting data
        data = {"job": job_data, "plugin": plugin_data}
        instance.data["deadlineData"] = data
