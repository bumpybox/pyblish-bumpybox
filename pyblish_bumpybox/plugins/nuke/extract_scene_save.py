from pyblish_bumpybox import plugin


class ExtractSceneSave(plugin.InstancePlugin):
    """ Saves the scene before extraction. """

    order = plugin.ExtractorOrder - 0.49
    families = ["source"]
    label = "Scene Save"
    targets = ["default", "process"]

    def process(self, instance):
        import nuke
        nuke.scriptSave()
