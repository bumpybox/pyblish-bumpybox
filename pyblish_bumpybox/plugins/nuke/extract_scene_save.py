from pyblish import api


class ExtractSceneSave(api.ContextPlugin):
    """ Saves the scene before extraction. """

    order = api.ExtractorOrder - 0.49
    families = ["source"]
    label = "Scene Save"
    targets = ["default", "process"]

    def process(self, instance):
        import nuke
        nuke.scriptSave()
