from pyblish import api
from pyblish_bumpybox import inventory


class ExtractSceneSave(api.ContextPlugin):
    """ Saves the active scene file """

    order = inventory.get_order(__file__, "ExtractSceneSave")
    families = ["scene"]
    label = "Scene Save"
    hosts = ["houdini"]

    def process(self, instance):
        import hou
        hou.hipFile.save()
