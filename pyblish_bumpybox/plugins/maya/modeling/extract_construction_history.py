from pyblish import api
from pyblish_bumpybox import inventory


class ExtractConstructionHistory(api.InstancePlugin):
    """ Option to extract the with/without construction history. """

    order = inventory.get_order(__file__, "ExtractConstructionHistory")
    families = ["mayaAscii", "mayaBinary"]
    optional = True
    label = "Remove Construction History"
    hosts = ["maya"]
    targets = ["process.local"]

    def process(self, instance):

        instance.data["constructionHistory"] = False
