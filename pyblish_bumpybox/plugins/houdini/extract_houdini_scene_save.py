import hou
import pyblish.api


class ExtractHoudiniSceneSave(pyblish.api.InstancePlugin):
    """ Saves the active scene file """

    order = pyblish.api.ExtractorOrder - 0.1
    families = ["scene"]
    label = "Scene Save"
    hosts = ["houdini"]

    def process(self, instance):

        hou.hipFile.save()
