import os

import pyblish.api
import ftrack


class AppendFtrackDeadlineData(pyblish.api.InstancePlugin):

    label = "Ftrack/Deadline"
    families = ["render"]
    order = pyblish.api.ExtractorOrder

    def process(self, instance):

        job_data = {}
        plugin_data = {}
        if "deadlineData" in instance.data:
            job_data = instance.data["deadlineData"]["job"].copy()
            plugin_data = instance.data["deadlineData"]["plugin"].copy()

        comment = ""
        task = ftrack.Task(instance.context.data["ftrackData"]["Task"]["id"])
        for p in reversed(task.getParents()):
            comment += p.getName() + "."
        comment += os.path.basename(instance.context.data["currentFile"])
        comment = os.path.splitext(comment)[0] + "." + str(instance)
        comment = "Ftrack path: \"{0}\"".format(comment)

        job_data["Comment"] = comment

        # adding to instance
        data = {'job': job_data, 'plugin': plugin_data}
        instance.data["deadlineData"] = data
