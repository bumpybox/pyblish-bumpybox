from pyblish_bumpybox import plugin


class ExtractDisconnectAnimation(plugin.InstancePlugin):
    """ Option to extract the with/without animation. """

    order = plugin.ExtractorOrder - 0.1
    families = ["mayaAscii", "mayaBinary"]
    optional = True
    label = "Disconnect Animation"
    hosts = ["maya"]

    def process(self, instance):

        instance.data["disconnectAnimation"] = True
