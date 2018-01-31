from pyblish import api
from pyblish_bumpybox import inventory


class AppendFtrackAssetName(api.InstancePlugin):
    """ Appending "ftrackAssetName" """

    label = "Ftrack Asset Name"
    order = inventory.get_order(__file__, "AppendFtrackAssetName")

    def process(self, instance):

        # skipping if not launched from ftrack
        if "ftrackData" not in instance.context.data:
            return

        ftrack_data = instance.context.data["ftrackData"]

        asset_name = ftrack_data["Task"]["name"]
        instance.data["ftrackAssetName"] = asset_name
