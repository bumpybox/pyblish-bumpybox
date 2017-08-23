import nuke
import pyblish.api


class ExtractNukeSceneSave(pyblish.api.InstancePlugin):
    """ Saves the scene before extraction. """

    order = pyblish.api.ExtractorOrder - 0.49
    families = ["source"]
    label = "Scene Save"
    targets = ["default", "process"]

    def process(self, instance):

        nuke.scriptSave()
