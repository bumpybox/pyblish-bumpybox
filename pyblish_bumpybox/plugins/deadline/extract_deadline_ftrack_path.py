import pyblish.api
import ftrack


class ExtractDeadlineFtrackPath(pyblish.api.InstancePlugin):
    """ Extract Ftrack path for Deadline """

    order = pyblish.api.ExtractorOrder
    families = ["deadline"]
    label = "Ftrack Path"

    def process(self, instance):

        if not instance.context.has_data("ftrackData"):
            return

        job_data = {}
        plugin_data = {}
        if "deadlineData" in instance.data:
            job_data = instance.data["deadlineData"]["job"].copy()
            plugin_data = instance.data["deadlineData"]["plugin"].copy()

        # commenting to store full ftrack path
        comment = ""
        task = ftrack.Task(instance.context.data["ftrackData"]["Task"]["id"])
        for p in reversed(task.getParents()):
            comment += p.getName() + "/"
        comment += task.getName()
        comment = "Ftrack path: \"{0}\"".format(comment)

        job_data["Comment"] = comment

        # setting data
        data = {"job": job_data, "plugin": plugin_data}
        instance.data["deadlineData"] = data
