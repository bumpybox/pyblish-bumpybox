import os
import tempfile
import time

import pyblish.api
import hiero
import clique


class BumpyboxHieroExtractTranscode(pyblish.api.InstancePlugin):
    """ Transcode shots. """

    order = pyblish.api.ExtractorOrder
    families = ["transcode"]
    label = "Transcode"
    optional = True

    def process(self, instance):

        item = instance[0]

        # Get handles.
        handles = 0
        if "handles" in instance.data["families"]:
            for tag in instance[0].tags():
                data = tag.metadata().dict()
                if "handles" == data.get("tag.family", ""):
                    handles = int(data["tag.value"])

        # Get reverse, retime, first and last frame
        reverse = False
        if item.playbackSpeed() < 0:
            reverse = True

        first_frame = int(item.sourceIn() + 1) - handles
        first_frame_offset = 1
        last_frame = int(item.sourceOut() + 1) + handles
        last_frame_offset = last_frame - first_frame + 1
        if reverse:
            first_frame = int(item.sourceOut() + 1)
            first_frame_offset = 1
            last_frame = int(item.sourceIn() + 1)
            last_frame_offset = last_frame - first_frame + 1

        # Creating transcode Nuke script
        nukeWriter = hiero.core.nuke.ScriptWriter()

        root_node = hiero.core.nuke.RootNode(
            first_frame_offset,
            last_frame_offset
        )
        nukeWriter.addNode(root_node)

        item.addToNukeScript(
            script=nukeWriter,
            firstFrame=first_frame_offset,
            includeRetimes=True,
            retimeMethod="Frame",
            startHandle=handles,
            endHandle=handles
        )

        # Create Nuke script
        write_path = os.path.join(
            os.path.dirname(instance.context.data["currentFile"]),
            "workspace",
            item.parent().parent().name(),
            item.parent().name(),
            item.name() + ".%04d.jpeg"
        )

        frame_padding = len(str(last_frame))
        if frame_padding < 4:
            frame_padding = 4
        padding_string = "%{0}d".format(str(frame_padding).zfill(2))
        write_path = write_path.replace("%04d", padding_string)

        write_node = hiero.core.nuke.WriteNode(write_path)
        write_node.setKnob("file_type", "jpeg")
        write_node.setKnob("_jpeg_quality", "1")
        nukeWriter.addNode(write_node)

        script_path = os.path.join(tempfile.gettempdir(), item.name() + ".nk")
        nukeWriter.writeToDisk(script_path)

        # Execute Nuke script
        logFileName = write_path + ".log"
        process = hiero.core.nuke.executeNukeScript(
            script_path,
            open(logFileName, "w")
        )

        while process.poll() is None:
            time.sleep(0.5)

        # Create collection
        split = write_path.split(padding_string)
        collection = clique.Collection(
            head=split[0],
            tail=split[1],
            padding=frame_padding
        )
        for count in range(first_frame_offset, last_frame_offset + 1):
            collection.add(write_path % count)

        # Validate output and clean up
        os.remove(script_path)

        missing_files = []
        for f in collection:
            if not os.path.exists(f):
                missing_files.append(f)

        if missing_files:
            msg = "Files were not transcoded: {0}".format(missing_files)
            raise ValueError(msg)

        instance.data["transcodes"] = [collection]
        os.remove(logFileName)
