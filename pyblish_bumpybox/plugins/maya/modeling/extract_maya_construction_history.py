import pyblish.api


class ExtractMayaConstructionHistory(pyblish.api.InstancePlugin):
    """ Option to extract the with/without construction history. """

    order = pyblish.api.ExtractorOrder - 0.1
    families = ["mayaAscii", "mayaBinary"]
    optional = True
    label = "Remove Construction History"
    hosts = ["maya"]

    def process(self, instance):

        instance.data["constructionHistory"] = False
