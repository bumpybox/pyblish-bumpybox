import pyblish.api


class ExtractMayaDisconnectAnimation(pyblish.api.InstancePlugin):
    """ Option to extract the with/without animation. """

    order = pyblish.api.ExtractorOrder - 0.1
    families = ["mayaAscii", "mayaBinary"]
    optional = True
    label = "Disconnect Animation"
    hosts = ["maya"]

    def process(self, instance):

        instance.data["disconnectAnimation"] = True
