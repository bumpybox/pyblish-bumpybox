import pyblish.api


class ExtractNukeStudioBakedColorspace(pyblish.api.InstancePlugin):
    """Extracts movie with baked in luts"""

    order = pyblish.api.ExtractorOrder
    label = "Baked Colorspace"
    optional = True
    families = ["img", "mov"]
    hosts = ["nukestudio"]

    def process(self, instance):
        import os
        import time
        import hiero.core

        nukeWriter = hiero.core.nuke.ScriptWriter()

        item = instance.data["item"]

        handles = instance.data["handles"]

        seq = item.parent().parent()
        root_node = hiero.core.nuke.RootNode(
            item.timelineIn() - handles,
            item.timelineOut() + handles,
            fps=seq.framerate()
        )
        nukeWriter.addNode(root_node)

        item.addToNukeScript(
            script=nukeWriter,
            includeRetimes=True,
            retimeMethod="Frame",
            startHandle=handles,
            endHandle=handles
        )

        node = hiero.core.nuke.Node("ViewerProcess_1DLUT")
        nukeWriter.addNode(node)

        output_path = instance.data.get("output_path", "")
        if not output_path:
            output_path = instance.data["collection"].format("{head}{tail}")

        ext = os.path.splitext(output_path)[1]
        movie_path = output_path.replace(
            ext, "_baked_colorspace.mov"
        )
        write_node = hiero.core.nuke.WriteNode(movie_path.replace("\\", "/"))
        write_node.setKnob("file_type", "mov")
        write_node.setKnob("mov32_fps", seq.framerate())
        write_node.setKnob("raw", True)
        nukeWriter.addNode(write_node)

        path = output_path.replace(
            ext, "_baked_colorspace.nk"
        )
        nukeWriter.writeToDisk(path)

        logFileName = path.replace(".nk", ".log")
        process = hiero.core.nuke.executeNukeScript(
            path,
            open(logFileName, "w")
        )

        while process.poll() is None:
            time.sleep(0.5)

        assert os.path.exists(movie_path), "Creating baked colorspace failed."

        instance.data["baked_colorspace_movie"] = movie_path
