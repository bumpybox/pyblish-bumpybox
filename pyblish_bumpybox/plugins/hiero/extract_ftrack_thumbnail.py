import os
import time

import pyblish.api
import hiero


class BumpyboxHieroExtractFtrackThumbnail(pyblish.api.InstancePlugin):
    """ Creates thumbnails for ftrack shots and uploads them. """

    order = pyblish.api.ExtractorOrder + 0.1
    families = ["ftrack", "trackItem"]
    match = pyblish.api.Subset
    label = "Ftrack Thumbnail"
    optional = True
    active = False

    def process(self, instance):

        item = instance[0]
        shot = instance.data["ftrackShot"]

        nukeWriter = hiero.core.nuke.ScriptWriter()

        # Getting top most track with media.
        seq = item.parent().parent()
        item = seq.trackItemAt(item.timelineIn())

        root_node = hiero.core.nuke.RootNode(1, 1, fps=seq.framerate())
        nukeWriter.addNode(root_node)

        handles = instance.data["handles"]

        item.addToNukeScript(
            script=nukeWriter,
            firstFrame=1,
            includeRetimes=True,
            retimeMethod="Frame",
            startHandle=handles,
            endHandle=handles
        )

        input_path = item.source().mediaSource().fileinfos()[0].filename()
        filename = os.path.splitext(input_path)[0]
        filename += "_thumbnail.png"
        output_path = os.path.join(
            os.path.dirname(instance.context.data["currentFile"]),
            "workspace",
            os.path.basename(filename)
        )

        fmt = hiero.core.Format(300, 200, 1, "thumbnail")
        fmt.addToNukeScript(script=nukeWriter)

        write_node = hiero.core.nuke.WriteNode(output_path)
        write_node.setKnob("file_type", "png")
        nukeWriter.addNode(write_node)

        script_path = output_path.replace(".png", ".nk")
        nukeWriter.writeToDisk(script_path)
        logFileName = output_path.replace(".png", ".log")
        process = hiero.core.nuke.executeNukeScript(
            script_path,
            open(logFileName, "w")
        )

        while process.poll() is None:
            time.sleep(0.5)

        if os.path.exists(output_path):
            self.log.info("Thumbnail rendered successfully!")

            # Creating thumbnail
            shot.createThumbnail(output_path)
        else:
            self.log.error("Thumbnail failed to render")
