import pyblish.api
import ftrack


class AppendFtrackAudio(pyblish.api.ContextPlugin):

    label = "Ftrack Audio"
    order = pyblish.api.ExtractorOrder

    def process(self, context):

        # get audio file
        task = ftrack.Task(context.data["ftrackData"]["Task"]["id"])
        try:
            asset = task.getParent().getAsset("audio", "audio")
            component = asset.getVersions()[-1].getComponent()
            audio_file = component.getFilesystemPath()
            context.data["audio"] = audio_file
        except:
            self.log.warning("Couldn't find any audio file on Ftrack.")


class AppendFtrackData(pyblish.api.InstancePlugin):
    """ Appending ftrack component and asset type data """

    families = ["img.*", "mov.*"]
    # offset to piggy back from default collectors
    order = pyblish.api.CollectorOrder + 0.1

    def process(self, instance):

        # ftrack data
        if not instance.context.has_data("ftrackData"):
            return

        instance.data["ftrackComponents"] = {}
        asset_type = instance.data["family"].split(".")[0]
        instance.data["ftrackAssetType"] = asset_type
