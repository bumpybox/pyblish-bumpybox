from pyblish import api
from pyblish_bumpybox import inventory


class ExtractSceneSave(api.InstancePlugin):
    """ Saves the scene before extraction. """

    order = inventory.get_order(__file__, "ExtractSceneSave")
    families = ["source"]
    label = "Scene Save"
    targets = ["default", "process"]

    def nuke_save(self):
        import nuke
        nuke.scriptSave()

    def maya_save(self):
        import pymel
        pymel.core.saveFile(force=True)

    def nukestudio_save(self, path):
        import hiero
        hiero.ui.activeSequence().project().save()

    def process(self, instance):
        from pyblish import api

        application_save = {
            "nukestudio": self.nukestudio_save,
            "nuke": self.nuke_save,
            "maya": self.maya_save
        }
        application_save[api.current_host()]()
