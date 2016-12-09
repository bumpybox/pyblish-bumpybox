import pyblish.api


class BumpyboxFtrackValidateAsset(pyblish.api.ContextPlugin):
    """ Appending ftrack asset type and asset name data.

    Currently a ContextPlugin because if an instance is unpublishable, it won't
    get processed correctly. So we are forcing the data onto the instances.
    """

    order = pyblish.api.ValidatorOrder - 0.49
    label = "Asset"
    families = ["local", "output"]

    def process(self, context):

        for instance in context:

            # Skipping invalid instances
            families = instance.data.get("families", [])
            if not (set(self.families) & set(families)):
                continue

            # assign components to activate processing
            components = instance.data.get("ftrackComponents", {})
            instance.data["ftrackComponents"] = components

            # assigning asset type
            families = instance.data.get("families", [])
            if "img" in families:
                instance.data["ftrackAssetType"] = "img"
            if "cache" in families:
                instance.data["ftrackAssetType"] = "cache"
            if "render" in families:
                instance.data["ftrackAssetType"] = "render"
            if "scene" in families:
                instance.data["ftrackAssetType"] = "scene"

            # skipping if not launched from ftrack
            if "ftrackData" not in instance.context.data:
                return

            # assigning asset name
            ftrack_data = instance.context.data["ftrackData"]
            asset_name = ftrack_data["Task"]["name"]
            instance.data["ftrackAssetName"] = asset_name
