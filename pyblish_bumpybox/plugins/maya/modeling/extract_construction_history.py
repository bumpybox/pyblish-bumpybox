from pyblish_bumpybox import plugin


class ExtractConstructionHistory(plugin.InstancePlugin):
    """ Option to extract the with/without construction history. """

    order = plugin.ExtractorOrder - 0.1
    families = ["mayaAscii", "mayaBinary"]
    optional = True
    label = "Remove Construction History"
    hosts = ["maya"]

    def process(self, instance):

        instance.data["constructionHistory"] = False
