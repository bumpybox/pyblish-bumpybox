import os

import pyblish.api
import hiero
import pipeline_schema


class ExtractNuke(pyblish.api.InstancePlugin):
    """ Extract nuke script """

    families = ["nuke"]
    label = "Nuke Script"
    order = pyblish.api.ExtractorOrder + 0.1

    def process(self, instance):

        item = instance[0]
        file_path = item.source().mediaSource().fileinfos()[0].filename()
        fps = item.sequence().framerate().toFloat()
        handles = instance.data["handles"]

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

        # creating exr transcode nuke script
        nukeWriter = hiero.core.nuke.ScriptWriter()

        root_node = hiero.core.nuke.RootNode(first_frame_offset,
                                             last_frame_offset)
        nukeWriter.addNode(root_node)

        width = item.parent().parent().format().width()
        height = item.parent().parent().format().height()

        item.addToNukeScript(script=nukeWriter, firstFrame=first_frame_offset,
                             includeRetimes=True, retimeMethod="Frame",
                             startHandle=handles, endHandle=handles)

        # get version data
        version = 1
        if "version" in instance.context.data:
            version = instance.context.data["version"]

        # expected path
        data = pipeline_schema.get_data()
        data["version"] = version
        data["extension"] = "exr"
        data["output_type"] = "img"
        data["name"] = str(instance)
        write_path = pipeline_schema.get_path("output_sequence", data)

        write_node = hiero.core.nuke.WriteNode(write_path)
        write_node.setKnob("file_type", "exr")
        write_node.setKnob("metadata", "all metadata")
        nukeWriter.addNode(write_node)

        data["extension"] = "nk"
        script_path = pipeline_schema.get_path("temp_file", data)
        nukeWriter.writeToDisk(script_path)

        # adding deadline data
        job_data = {"Group": "nuke_9", "Pool": "medium", "Plugin": "Nuke",
                    "OutputFilename0": write_path, "ChunkSize": 10,
                    "Frames": "{0}-{1}".format(first_frame_offset,
                                               last_frame_offset),
                    "LimitGroups": "nuke"}

        name = os.path.basename(instance.context.data["currentFile"])
        name = "{0} - {1}".format(os.path.splitext(name)[0], str(instance))
        job_data["Name"] = name

        plugin_data = {"NukeX": False, "Version": "9.0",
                       "EnforceRenderOrder": True}

        instance.data["deadlineData"] = {"job": job_data,
                                         "plugin": plugin_data,
                                         "auxiliaryFiles": [script_path]}

        # creating shot nuke script
        nukeWriter = hiero.core.nuke.ScriptWriter()

        # root node
        root_node = hiero.core.nuke.RootNode(first_frame_offset,
                                             last_frame_offset, fps=fps)
        if retime:
            last_frame = abs(int(round(last_frame_offset /
                                       item.playbackSpeed())))
            root_node = hiero.core.nuke.RootNode(first_frame_offset,
                                                 last_frame, fps=fps)
        fmt = item.parent().parent().format()
        root_node.setKnob("format", "{0} {1}".format(fmt.width(),
                                                     fmt.height()))
        nukeWriter.addNode(root_node)

        # primary read node
        read_node = hiero.core.nuke.ReadNode(write_path,
                                             width=width,
                                             height=height,
                                             firstFrame=first_frame_offset,
                                             lastFrame=last_frame_offset)
        nukeWriter.addNode(read_node)
        last_node = read_node

        if reverse or retime:

            last_frame = last_frame_offset
            if retime:
                last_frame = abs(int(round(last_frame_offset /
                                           item.playbackSpeed())))
            retime_node = hiero.core.nuke.RetimeNode(first_frame_offset,
                                                     last_frame_offset,
                                                     first_frame_offset,
                                                     last_frame,
                                                     reverse=reverse)
            retime_node.setKnob("shutter", 0)
            retime_node.setInputNode(0, read_node)
            nukeWriter.addNode(retime_node)
            last_node = retime_node

        data["extension"] = "exr"
        temp_file = pipeline_schema.get_path("temp_file", data)
        write_node = hiero.core.nuke.WriteNode(temp_file, inputNode=last_node)
        write_node.setKnob("file_type", "exr")
        write_node.setKnob("metadata", "all metadata")
        nukeWriter.addNode(write_node)

        # secondary read nodes
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
            read_node = hiero.core.nuke.ReadNode(src, width=width,
                                                 height=height,
                                                 firstFrame=in_frame,
                                                 lastFrame=out_frame)
            nukeWriter.addNode(read_node)

            retime_node = hiero.core.nuke.RetimeNode(in_frame, out_frame,
                                                     first_frame_offset,
                                                     last_frame)
            retime_node.setKnob("shutter", 0)
            retime_node.setInputNode(0, read_node)
            nukeWriter.addNode(retime_node)

        # get file path
        data["extension"] = "nk"
        file_path = pipeline_schema.get_path("output_file", data)

        # create directories
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))

        # create nuke script
        nukeWriter.writeToDisk(file_path)

        # publishing to ftrack
        asset = instance.data["ftrackShot"].createAsset(str(instance), "scene")

        # removing existing version
        for v in asset.getVersions():
            if v.getVersion() == instance.context.data["version"]:
                v.delete()

        # creating new version
        version = asset.createVersion()
        version.set("version", instance.context.data["version"])
        version.createComponent(name="nuke", path=file_path)
        version.publish()
