import os
import subprocess

import pyblish.api


class RepairMovie(pyblish.api.Action):

    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):

        # Get the errored instances
        failed = []
        for result in context.data["results"]:
            if (result["error"] is not None and result["instance"] is not None
               and result["instance"] not in failed):
                failed.append(result["instance"])

        # Apply pyblish.logic to get the instances for the plug-in
        instances = pyblish.api.instances_by_plugin(failed, plugin)

        for instance in instances:

            cls_instance = ValidateMovie()
            cls_instance.produce_movie(instance)


class ValidateMovie(pyblish.api.InstancePlugin):

    order = pyblish.api.ValidatorOrder
    targets = ["default"]
    families = ["img"]
    optional = True
    label = "Review Movie"
    actions = [RepairMovie]

    def process(self, instance):

        collection = instance.data["collection"]
        path = collection.format("{head}.mov")

        msg = "Review movie \"{0}\" does not exist.".format(path)
        assert os.path.exists(path), msg

    def produce_movie(self, instance):

        collection = instance.data["collection"]

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


class ExtractMovie(ValidateMovie):
    """Extracts movie from image sequence.

    Offset to get images to transcode from.
    """

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

        self.produce_movie(instance)
