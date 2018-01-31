from pyblish import api
from pyblish_bumpybox import inventory


class ExtractNukeScript(api.InstancePlugin):
    """ Extract Nuke script """

    families = ["nuke"]
    label = "Nuke Script"
    order = inventory.get_order(__file__, "ExtractNukeScript")
    optional = True
    hosts = ["hiero"]

    def process(self, instance):
        import os

        import hiero
        import clique

        item = instance[0]
        file_path = item.source().mediaSource().fileinfos()[0].filename()
        fps = item.sequence().framerate().toFloat()

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

        retime = False
        if item.playbackSpeed() != 1.0:
            retime = True

        first_frame = int(item.sourceIn() + 1) - handles
        first_frame_offset = 1
        last_frame = int(item.sourceOut() + 1) + handles
        last_frame_offset = last_frame - first_frame + 1
        if reverse:
            first_frame = int(item.sourceOut() + 1)
            first_frame_offset = 1
            last_frame = int(item.sourceIn() + 1)
            last_frame_offset = last_frame - first_frame + 1

        # Get resolution
        width = item.parent().parent().format().width()
        height = item.parent().parent().format().height()

        # Creating shot nuke script
        nukeWriter = hiero.core.nuke.ScriptWriter()

        # Root node
        root_node = hiero.core.nuke.RootNode(
            first_frame_offset,
            last_frame_offset,
            fps=fps
        )
        if retime:
            last_frame = abs(int(round(
                last_frame_offset / item.playbackSpeed()
            )))
            root_node = hiero.core.nuke.RootNode(
                first_frame_offset,
                last_frame,
                fps=fps
            )
        fmt = item.parent().parent().format()
        root_node.setKnob("format", "{0} {1}".format(
            fmt.width(),
            fmt.height()
        ))
        nukeWriter.addNode(root_node)

        # Primary read node
        read_node = hiero.core.nuke.ReadNode(
            file_path,
            width=width,
            height=height,
            firstFrame=first_frame,
            lastFrame=last_frame + 1
        )
        read_node.setKnob("frame_mode", 2)
        read_node.setKnob("frame", str(first_frame - 1))
        nukeWriter.addNode(read_node)
        last_node = read_node

        if reverse or retime:

            last_frame = last_frame_offset
            if retime:
                last_frame = abs(int(round(
                    last_frame_offset / item.playbackSpeed()
                )))
            retime_node = hiero.core.nuke.RetimeNode(
                first_frame_offset,
                last_frame_offset,
                first_frame_offset,
                last_frame,
                reverse=reverse
            )
            retime_node.setKnob("shutter", 0)
            retime_node.setInputNode(0, read_node)
            nukeWriter.addNode(retime_node)
            last_node = retime_node

        # Create write node
        write_path = os.path.join(
            os.path.dirname(instance.context.data["currentFile"]),
            "workspace",
            item.parent().parent().name(),
            item.parent().name(),
            item.name() + ".%04d.exr"
        )

        frame_padding = len(str(last_frame))
        if frame_padding < 4:
            frame_padding = 4
        padding_string = "%{0}d".format(str(frame_padding).zfill(2))
        write_path = write_path.replace("%04d", padding_string)

        write_node = hiero.core.nuke.WriteNode(write_path, inputNode=last_node)
        write_node.setKnob("file_type", "exr")
        write_node.setKnob("metadata", "all metadata")
        write_node.setName(instance.data["name"])
        nukeWriter.addNode(write_node)

        # Secondary read nodes
        seq = item.parent().parent()
        time_in = item.timelineIn()
        time_out = item.timelineOut()

        items = []
        for count in range(time_in, time_out):
            items.extend(seq.trackItemsAt(count))

        items = list(set(items))
        items.remove(item)

        last_frame = abs(int(round(last_frame_offset /
                                   item.playbackSpeed())))

        for i in items:
            src = i.source().mediaSource().fileinfos()[0].filename()
            in_frame = i.mapTimelineToSource(time_in) + 1 - handles
            out_frame = i.mapTimelineToSource(time_out) + 1 + handles
            read_node = hiero.core.nuke.ReadNode(
                src,
                width=width,
                height=height,
                firstFrame=in_frame,
                lastFrame=out_frame
            )
            nukeWriter.addNode(read_node)

            retime_node = hiero.core.nuke.RetimeNode(
                in_frame,
                out_frame,
                first_frame_offset,
                last_frame
            )
            retime_node.setKnob("shutter", 0)
            retime_node.setInputNode(0, read_node)
            nukeWriter.addNode(retime_node)

        # Get file path
        file_path = os.path.join(
            os.path.dirname(instance.context.data["currentFile"]),
            "workspace",
            item.parent().parent().name(),
            item.parent().name(),
            item.name() + ".0001.nk"
        )

        # Create directories
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))

        # Create nuke script
        nukeWriter.writeToDisk(file_path)
        self.log.info("Writing Nuke script to: \"%s\"" % file_path)

        collection = clique.Collection(
            head=file_path.replace("0001.nk", ""), padding=4, tail=".nk"
        )
        collection.add(file_path)
        instance.data["collection"] = collection
