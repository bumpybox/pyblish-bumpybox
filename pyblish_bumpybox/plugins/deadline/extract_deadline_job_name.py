import os

import pyblish.api


class ExtractDeadlineJobName(pyblish.api.InstancePlugin):
    """ Appending Deadline job name to all instances. """

    families = ["deadline"]
    order = pyblish.api.ExtractorOrder
    label = "Deadline Job Name"

    def process(self, instance):

        data = instance.data.get(
            "deadlineData", {"job": {}, "plugin": {}}
        )

        data["job"]["Name"] = "{0} - {1}".format(
            os.path.basename(instance.context.data["currentFile"]),
            instance
        )

        instance.data["deadlineData"] = data
