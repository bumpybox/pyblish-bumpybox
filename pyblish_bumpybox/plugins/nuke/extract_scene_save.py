from pyblish import api
from pyblish_bumpybox import inventory


class ExtractSceneSave(api.ContextPlugin):
    """ Saves the scene before extraction. """

    order = inventory.get_order(__file__, "ExtractSceneSave")
    families = ["source"]
    label = "Scene Save"
    targets = ["default", "process"]

    def process(self, instance):
        import nuke
        nuke.scriptSave()
