import hou
import pyblish.api


class SaveScene(pyblish.api.InstancePlugin):
    """ Saves the active scene file """

    order = pyblish.api.ExtractorOrder - 0.1
    families = ['scene']
    label = 'Scene Save'

    def process(self, instance):

        hou.hipFile.save()
