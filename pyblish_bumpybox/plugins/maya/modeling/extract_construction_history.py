from pyblish import api


class ExtractConstructionHistory(api.ContextPlugin):
    """ Option to extract the with/without construction history. """

    order = api.ExtractorOrder - 0.1
    families = ["mayaAscii", "mayaBinary"]
    optional = True
    label = "Remove Construction History"
    hosts = ["maya"]

    def process(self, instance):

        instance.data["constructionHistory"] = False
