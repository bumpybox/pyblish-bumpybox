import os
import subprocess

import pyblish.api


class ExtractMovie(pyblish.api.InstancePlugin):
    """Extracts movie from image sequence.

    Offset to get images to transcode from.
    """

    families = ["img"]
    order = pyblish.api.ExtractorOrder + 0.1
    label = "Movie"
    optional = True
    targets = ["process.local"]

    def process(self, instance):

        collection = instance.data.get("collection", [])

        if not list(collection):
            msg = "Skipping \"{0}\" because no frames was found."
            self.log.info(msg.format(instance.data["name"]))
            return

        if len(list(collection)) == 1:
            msg = "Skipping \"{0}\" because only a single frame was found."
            self.log.info(msg.format(instance.data["name"]))
            return

        # Start number needs to always be the first file of the existing
        # frames, in order to ensure the full movie gets exported.
        root = os.path.dirname(collection.format())
        indexes = []
        for f in os.listdir(root):
            file_path = os.path.join(root, f).replace("\\", "/")
            match = collection.match(file_path)
            if match:
                indexes.append(int(match.groupdict()["index"]))

        args = [
            "ffmpeg", "-y", "-gamma", "2.2",
            "-framerate", str(instance.context.data["framerate"]),
            "-start_number", str(min(indexes)),
            "-i", collection.format("{head}{padding}{tail}"),
            "-q:v", "0", "-pix_fmt", "yuv420p", "-vf",
            "scale=trunc(iw/2)*2:trunc(ih/2)*2,colormatrix=bt601:bt709",
            "-timecode", "00:00:00:01",
            collection.format("{head}.mov")
        ]

        self.log.debug("Executing args: {0}".format(args))

        # Can't use subprocess.check_output, cause Houdini doesn't like that.
        p = subprocess.Popen(args, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, stdin=subprocess.PIPE)

        output = p.communicate()[0]

        if p.returncode != 0:
            raise ValueError(output)

        self.log.debug(output)


class ExtractReadMovie(ExtractMovie):
    """Extracts movie from read nodes."""

    families = ["read"]
    order = pyblish.api.ExtractorOrder
    label = "Read Movie"
    optional = True
    targets = ["default"]
