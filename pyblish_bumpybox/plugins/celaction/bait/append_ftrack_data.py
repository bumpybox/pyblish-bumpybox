from pyblish_bumpybox import plugin


class AppendFtrackAudio(plugin.ContextPlugin):

    label = "Ftrack Audio"
    order = plugin.ExtractorOrder

    def process(self, context):
        import ftrack

        # get audio file
        task = ftrack.Task(context.data["ftrackData"]["Task"]["id"])
        try:
            asset = task.getParent().getAsset("audio", "audio")
            component = asset.getVersions()[-1].getComponent()
            audio_file = component.getFilesystemPath()
            context.data["audio"] = audio_file
        except:
            self.log.warning("Couldn't find any audio file on Ftrack.")


class AppendFtrackData(plugin.InstancePlugin):
    """ Appending ftrack component and asset type data """

    families = ["img.*", "mov.*"]
    # offset to piggy back from default collectors
    order = plugin.CollectorOrder + 0.1

    def process(self, instance):

        # ftrack data
        if not instance.context.has_data("ftrackData"):
            return

        instance.data["ftrackComponents"] = {}
        asset_type = instance.data["family"].split(".")[0]
        instance.data["ftrackAssetType"] = asset_type
