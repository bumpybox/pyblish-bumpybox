from pyblish import api


class ExtractSceneSave(api.ContextPlugin):
    """ Saves the active scene file """

    order = api.ExtractorOrder - 0.1
    families = ["scene"]
    label = "Scene Save"
    hosts = ["houdini"]

    def process(self, instance):
        import hou
        hou.hipFile.save()
