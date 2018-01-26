from pyblish import api


class ExtractDisconnectAnimation(api.ContextPlugin):
    """ Option to extract the with/without animation. """

    order = api.ExtractorOrder - 0.1
    families = ["mayaAscii", "mayaBinary"]
    optional = True
    label = "Disconnect Animation"
    hosts = ["maya"]

    def process(self, instance):

        instance.data["disconnectAnimation"] = True
