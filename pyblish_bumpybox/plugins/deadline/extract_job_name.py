from pyblish_bumpybox import plugin


class ExtractJobName(plugin.InstancePlugin):
    """ Appending Deadline job name to all instances. """

    families = ["deadline"]
    order = plugin.ExtractorOrder
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
