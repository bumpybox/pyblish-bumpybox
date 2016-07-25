import os

import hou
import pyblish.api


class AppendDeadlineDataBumpybox(pyblish.api.InstancePlugin):
    """ Appending Deadline data to houdini farm instances """

    families = ["img.farm.*", "cache.farm.*"]
    order = pyblish.api.ExtractorOrder

    def process(self, instance):

        job_data = {}
        plugin_data = {}
        if "deadlineData" in instance.data:
            job_data = instance.data["deadlineData"]["job"].copy()
            plugin_data = instance.data["deadlineData"]["plugin"].copy()

        # setting job data
        name = os.path.basename(instance.context.data["currentFile"])
        name = os.path.splitext(name)[0]
        job_data["Name"] = name + " - " + str(instance)
        job_data["Pool"] = "medium"
        version = hou.applicationVersion()
        job_data["Group"] = "houdini_{0}_{1}".format(version[0], version[1])
        job_data["LimitGroups"] = "houdini"

        # setting data
        data = {"job": job_data, "plugin": plugin_data}
        instance.data["deadlineData"] = data
