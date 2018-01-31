from pyblish import api
from pyblish_bumpybox import inventory


class ExtractJobName(api.InstancePlugin):
    """ Appending Deadline job name to all instances. """

    families = ["deadline"]
    order = inventory.get_order(__file__, "ExtractJobName")
    label = "Deadline Job Name"

    def process(self, instance):
        import os

        data = instance.data.get(
            "deadlineData", {"job": {}, "plugin": {}}
        )

        data["job"]["Name"] = "{0} - {1}".format(
            os.path.basename(instance.context.data["currentFile"]),
            instance
        )

        instance.data["deadlineData"] = data
