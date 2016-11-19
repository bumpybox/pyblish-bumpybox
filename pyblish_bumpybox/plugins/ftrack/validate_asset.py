import pyblish.api


class BumpyboxFtrackValidateAsset(pyblish.api.InstancePlugin):
    """ Appending ftrack asset type and asset name data """

    order = pyblish.api.ValidatorOrder - 0.49
    families = ["local", "scene"]
    label = "Asset"

    def process(self, instance):

        # assign components to activate processing
        components = instance.data.get("ftrackComponents", {})
        instance.data["ftrackComponents"] = components

        # assigning asset type
        families = instance.data.get("families", [])
        instance.data["ftrackAssetType"] = "upload"
        if "img" in families:
            instance.data["ftrackAssetType"] = "img"
        if "cache" in families:
            instance.data["ftrackAssetType"] = "cache"
        if "render" in families:
            instance.data["ftrackAssetType"] = "render"

        if instance.data["family"] == "scene":
            instance.data["ftrackAssetType"] = "scene"

        # skipping if not launched from ftrack
        if "ftrackData" not in instance.context.data:
            return

        # assigning asset name
        ftrack_data = instance.context.data["ftrackData"]
        asset_name = ftrack_data["Task"]["name"]
        instance.data["ftrackAssetName"] = asset_name
