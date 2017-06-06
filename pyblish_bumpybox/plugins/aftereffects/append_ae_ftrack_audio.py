import pyblish.api
import ftrack


class AppendAEFtrackAudio(pyblish.api.ContextPlugin):

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
