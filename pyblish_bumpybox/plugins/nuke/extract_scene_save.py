import nuke
import pyblish.api


@pyblish.api.log
class ExtractSceneSave(pyblish.api.Extractor):
    """
    """

    order = pyblish.api.Extractor.order - 0.1
    families = ['scene']
    label = 'Scene Save'

    def process(self, instance):

        nuke.scriptSave()
