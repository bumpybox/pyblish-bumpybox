import os
import subprocess

import pymel.core
import pyblish.api
from capture import capture
import clique


class BumpyboxMayaExtractPlayblast(pyblish.api.InstancePlugin):
    """ Extracts playblast. """

    order = pyblish.api.ExtractorOrder
    families = ["playblast"]
    optional = True
    label = "Playblast"
    hosts = ["maya"]

    def getFPS(self):

        options = {"pal": 25, "game": 15, "film": 24, "ntsc": 30, "show": 48,
                   "palf": 50, "ntscf": 60}

        option = pymel.core.general.currentUnit(q=True, t=True)

        return options[option]

    def process(self, instance):

        filename = instance.data["collection"].format("{head}")[:-1]
        ext = "png"

        # Create temporary image files
        capture(
            instance[0].getTransform().name(),
            filename=filename,
            viewer=False,
            show_ornaments=False,
            overwrite=True,
            off_screen=True,
            format="image",
            compression=ext,
            viewport_options={"rendererName": "vp2Renderer"},
            viewport2_options={
                "multiSampleEnable": True, "multiSampleCount": 8
            }
        )

        # Create movie from images
        subprocess.check_output([
            "ffmpeg", "-y", "-gamma", "2.2",
            "-framerate", str(self.getFPS()),
            "-start_number", str(list(instance.data["collection"].indexes)[0]),
            "-i", filename + ".%04d." + ext,
            "-preset", "veryslow", "-crf", "0",
            "-pix_fmt", "yuv420p", "-vf",
            "scale=trunc(iw/2)*2:trunc(ih/2)*2,colormatrix=bt601:bt709",
            "-timecode", "00:00:00:01",
            list(instance.data["collection"])[0]
        ])

        # Clean up temporary image files
        collection = clique.Collection(
            head=instance.data["collection"].format("{head}"),
            padding=4,
            tail="." + ext
        )

        workspace = os.path.dirname(collection.format())
        for f in os.listdir(workspace):
            filename = os.path.join(workspace, f)
            if collection.match(filename):
                os.remove(filename)
