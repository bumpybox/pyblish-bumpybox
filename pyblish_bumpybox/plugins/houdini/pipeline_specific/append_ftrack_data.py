import pyblish.api


class AppendFtrackData(pyblish.api.InstancePlugin):
    """ Appending ftrack component and asset type data """

    families = ["img.*", "cache.*"]
    # offset to piggy back from default collectors
    order = pyblish.api.CollectorOrder + 0.2

    def process(self, instance):

        # ftrack data
        if not instance.context.has_data("ftrackData"):
            return

        instance.data["ftrackComponents"] = {}

        if "img.*" in instance.data["families"]:
            instance.data["ftrackAssetType"] = "img"
        if "cache.*" in instance.data["families"]:
            instance.data["ftrackAssetType"] = "cache"
