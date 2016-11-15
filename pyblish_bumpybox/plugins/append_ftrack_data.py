import pyblish.api


class AppendFtrackAssetData(pyblish.api.InstancePlugin):
    """ Appending ftrack asset type and asset name data """

    order = pyblish.api.ValidatorOrder - 0.49

    def process(self, instance):

        # assign components to activate processing
        components = instance.data.get("ftrackComponents", {})
        instance.data["ftrackComponents"] = components

        # assigning asset type
        if "families" in instance.data:
            if "img.*" in instance.data["families"]:
                instance.data["ftrackAssetType"] = "img"
            if "cache.*" in instance.data["families"]:
                instance.data["ftrackAssetType"] = "cache"

        if instance.data["family"] == "scene":
            instance.data["ftrackAssetType"] = "scene"

        # skipping if not launched from ftrack
        if "ftrackData" not in instance.context.data:
            return

        # assigning asset name
        ftrack_data = instance.context.data["ftrackData"]
        asset_name = ftrack_data["Task"]["name"]
        instance.data["ftrackAssetName"] = asset_name


class AppendFtrackComponents(pyblish.api.InstancePlugin):
    """ Appending output files from local extraction as components. """

    order = pyblish.api.ExtractorOrder + 0.49

    def process(self, instance):

        if "outputPath" in instance.data:
            components = instance.data.get("ftrackComponents", {})
            data = {"path": instance.data["outputPath"],
                    "overwrite": True}
            components[str(instance)] = data
            instance.data["ftrackComponents"] = components
