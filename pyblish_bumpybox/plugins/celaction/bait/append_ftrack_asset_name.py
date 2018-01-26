from pyblish_bumpybox import plugin


class AppendFtrackAssetName(plugin.InstancePlugin):
    """ Appending "ftrackAssetName" """

    label = "Ftrack Asset Name"
    order = plugin.CollectorOrder + 0.1

    def process(self, instance):

        # skipping if not launched from ftrack
        if "ftrackData" not in instance.context.data:
            return

        ftrack_data = instance.context.data["ftrackData"]

        asset_name = ftrack_data["Task"]["name"]
        instance.data["ftrackAssetName"] = asset_name
