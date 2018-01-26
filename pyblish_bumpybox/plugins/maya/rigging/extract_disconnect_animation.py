from pyblish import api
from pyblish_bumpybox import inventory


class ExtractDisconnectAnimation(api.ContextPlugin):
    """ Option to extract the with/without animation. """

    order = inventory.get_order(__file__, "ExtractDisconnectAnimation")
    families = ["mayaAscii", "mayaBinary"]
    optional = True
    label = "Disconnect Animation"
    hosts = ["maya"]

    def process(self, instance):

        instance.data["disconnectAnimation"] = True
