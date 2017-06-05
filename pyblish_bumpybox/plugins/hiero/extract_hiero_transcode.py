import os
import time

import pyblish.api
import hiero
import clique


class ExtractHieroTranscode(pyblish.api.InstancePlugin):
    """ Transcode shots. """

    order = pyblish.api.ExtractorOrder
    families = ["transcode"]
    label = "Transcode"
    optional = True

    def process(self, instance):

        collections = []
        transcode_tags = instance.data.get("transcodeTags", [])
        for tag in instance[0].tags():

            if tag.name() not in transcode_tags:
                continue

            write_path = os.path.join(
                os.path.dirname(instance.context.data["currentFile"]),
                "workspace",
                instance[0].parent().parent().name(),
                instance[0].parent().name(),
                "{0}_{1}.%04d.".format(instance[0].name(), tag.name())
            )

            if tag.name() == "jpeg":
                write_path += "jpeg"

            if tag.name() in ["h264", "h264_half"]:
                write_path += "mov"

            if tag.name() in ["jpeg", "h264", "h264_half"]:
                collections.append(
                    self.transcode(instance, write_path, tag.name())
                )

        instance.data["transcodes"] = collections

    def transcode(self, instance, write_path, tag_type):

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
        frame_padding = len(str(last_frame))
        if frame_padding < 4:
            frame_padding = 4
        padding_string = "%{0}d".format(str(frame_padding).zfill(2))
        write_path = write_path.replace("%04d", padding_string)

        write_node = hiero.core.nuke.WriteNode(write_path)

        if tag_type == "jpeg":
            write_node.setKnob("file_type", "jpeg")
            write_node.setKnob("_jpeg_quality", "1")
        if tag_type in ["h264", "h264_half"]:
            write_node.setKnob("file_type", "mov")
            write_node.setKnob("meta_codec", "avc1")
            write_node.setKnob(
                "mov32_fps", item.parent().parent().framerate().toFloat()
            )
        if tag_type.endswith("_half"):
            reformat_node = hiero.core.nuke.ReformatNode(
                scale=0.5, to_type="scale"
            )
            nukeWriter.addNode(reformat_node)

        nukeWriter.addNode(write_node)

        script_path = os.path.join(
            os.path.dirname(instance.context.data["currentFile"]),
            "workspace",
            "{0}_{1}.nk".format(item.name(), tag_type)
        )
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

        if write_path.endswith(".mov"):
            collection.add(write_path % last_frame_offset)
        else:
            for count in range(first_frame_offset, last_frame_offset + 1):
                collection.add(write_path % count)

        # Validate output and clean up
        missing_files = []
        for f in collection:
            if not os.path.exists(f):
                missing_files.append(f)

        if missing_files:
            msg = "Files were not transcoded: {0}".format(missing_files)
            raise ValueError(msg)

        os.remove(logFileName)
        os.remove(script_path)
        collection.tag_type = tag_type

        return collection


class BumpyboxHieroExtractTranscodeJPEG(pyblish.api.InstancePlugin):
    """ Enable/Disable JPEG transcoding. """

    order = ExtractHieroTranscode.order - 0.1
    families = ["jpeg", "jpeg_half"]
    label = "Transcode JPEG"
    optional = True

    def process(self, instance):

        data = instance.data.get("transcodeTags", [])
        data.extend(["jpeg", "jpeg_half"])
        instance.data["transcodeTags"] = data


class BumpyboxHieroExtractTranscodeH264(pyblish.api.InstancePlugin):
    """ Enable/Disable h264 transcoding. """

    order = ExtractHieroTranscode.order - 0.1
    families = ["h264", "h264_half"]
    label = "Transcode H264"
    optional = True

    def process(self, instance):

        data = instance.data.get("transcodeTags", [])
        data.extend(["h264", "h264_half"])
        instance.data["transcodeTags"] = data
