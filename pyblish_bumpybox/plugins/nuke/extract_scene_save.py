import pyblish.api


class ExtractSceneSave(pyblish.api.InstancePlugin):
    """ Saves the scene before extraction. """

    order = pyblish.api.ExtractorOrder - 0.49
    families = ["source"]
    label = "Scene Save"
    targets = ["default", "process"]

    def process(self, instance):
        import nuke
        nuke.scriptSave()
