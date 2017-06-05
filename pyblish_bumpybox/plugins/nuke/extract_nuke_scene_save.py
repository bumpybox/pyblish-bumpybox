import nuke
import pyblish.api


class ExtractNukeSceneSave(pyblish.api.InstancePlugin):
    """ Saves the scene before extraction. """

    order = pyblish.api.ExtractorOrder - 0.49
    families = ["scene"]
    label = "Scene Save"

    def process(self, instance):

        nuke.scriptSave()
