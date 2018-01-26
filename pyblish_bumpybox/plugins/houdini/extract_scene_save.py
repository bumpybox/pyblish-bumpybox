from pyblish_bumpybox import plugin


class ExtractSceneSave(plugin.InstancePlugin):
    """ Saves the active scene file """

    order = plugin.ExtractorOrder - 0.1
    families = ["scene"]
    label = "Scene Save"
    hosts = ["houdini"]

    def process(self, instance):
        import hou
        hou.hipFile.save()
