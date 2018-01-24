import pyblish.api


class ExtractSceneSave(pyblish.api.InstancePlugin):
    """ Saves the active scene file """

    order = pyblish.api.ExtractorOrder - 0.1
    families = ["scene"]
    label = "Scene Save"
    hosts = ["houdini"]

    def process(self, instance):
        import hou
        hou.hipFile.save()
