import os
import subprocess

import pyblish.api
import filelink


class ValidateMovie(pyblish.api.InstancePlugin):
    """Validate environment is ready for extracting a movie."""

    order = pyblish.api.ValidatorOrder
    label = "Movie"
    optional = True
    families = ["img"]

    def process(self, instance):

        self.get_executable_path("ffmpeg")

    def get_executable_path(self, executable):
        """Returns the full path to an executable.

        Args:
            executable (str): The name of executable without extension.
        """

        def is_exe(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

        fpath, fname = os.path.split(executable)
        if fpath:
            if is_exe(executable):
                return fpath
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, executable)
                if is_exe(exe_file):
                    return exe_file
                if is_exe(exe_file + ".exe"):
                    return exe_file + ".exe"

        raise IOError("\"{0}\" executable not found.".format(executable))


class ExtractImgMovie(pyblish.api.InstancePlugin):
    """Extracts review movie from image sequence.

    Offset to get images to transcode from.
    """

    order = pyblish.api.ExtractorOrder + 0.1
    label = "Img > Review Movie"
    optional = True
    families = ["img"]

    def find_previous_index(self, index, indexes):
        """Finds the closest previous value in a list from a value."""

        data = []
        for i in indexes:
            if i >= index:
                continue
            data.append(index - i)

        return indexes[data.index(min(data))]

    def process(self, instance):

        collection = instance.data.get("collection", [])

        if not list(collection):
            msg = "Skipping \"{0}\" because no frames was found."
            self.log.warning(msg.format(instance.data["name"]))
            return

        collection = instance.data["collection"]

        # Temporary fill the missing frames.
        missing = collection.holes()
        if not collection.is_contiguous():
            pattern = collection.format("{head}{padding}{tail}")
            for index in missing.indexes:
                dst = pattern % index
                src_index = self.find_previous_index(
                    index, list(collection.indexes)
                )
                src = pattern % src_index

                filelink.create(src, dst)

        # Start number needs to always be the first file of the existing
        # frames, in order to ensure the full movie gets exported.
        # Also finding any LUT file to use.
        root = os.path.dirname(collection.format())
        lut_file = None
        for f in os.listdir(root):
            if f.endswith(".cube"):
                lut_file = f

        # Generate args.
        # Has to be yuv420p for compatibility with older players and smooth
        # playback. This does come with a sacrifice of more visible banding
        # issues.
        # -crf 18 is visually lossless.
        args = [
            "ffmpeg", "-y",
            "-start_number", str(min(collection.indexes)),
            "-framerate", str(instance.context.data["framerate"]),
            "-i", collection.format("{head}{padding}{tail}"),
            "-pix_fmt", "yuv420p",
            "-crf", "18",
            "-timecode", "00:00:00:01",
            "-vframes",
            str(max(collection.indexes) - min(collection.indexes) + 1)
        ]

        # Limit amount of video filters to reduce artifacts and banding.
        if lut_file:
            args.extend(["-vf", "lut3d={0}".format(lut_file)])

        args.append(collection.format("{head}.mov"))

        self.log.debug("Executing args: {0}".format(args))

        # Can't use subprocess.check_output, cause Houdini doesn't like that.
        p = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            cwd=os.path.dirname(args[-1])
        )

        output = p.communicate()[0]

        # Remove temporary frame fillers
        for f in missing:
            os.remove(f)

        if p.returncode != 0:
            raise ValueError(output)

        self.log.debug(output)


class ExtractMovMovie(pyblish.api.InstancePlugin):
    """Extracts review movie from movies."""

    order = pyblish.api.ExtractorOrder + 0.1
    label = "Movie > Review Movie"
    optional = True
    families = ["mov"]

    def process(self, instance):

        root = os.path.dirname(instance.data["output_path"])
        lut_file = None
        for f in os.listdir(root):
            if f.endswith(".cube"):
                lut_file = f

        # Generate args.
        # Has to be yuv420p for compatibility with older players and smooth
        # playback. This does come with a sacrifice of more visible banding
        # issues.
        args = [
            "ffmpeg", "-y",
            "-i", instance.data["output_path"],
            "-pix_fmt", "yuv420p",
            "-crf", "18",
            "-timecode", "00:00:00:01",
        ]

        # Limit amount of video filters to reduce artifacts and banding.
        if lut_file:
            args.extend(["-vf", "lut3d={0}".format(lut_file)])

        split = os.path.splitext(instance.data["output_path"])
        args.append(split[0] + "_review.mov")

        self.log.debug("Executing args: {0}".format(args))

        # Can't use subprocess.check_output, cause Houdini doesn't like that.
        p = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            cwd=os.path.dirname(args[-1])
        )

        output = p.communicate()[0]

        if p.returncode != 0:
            raise ValueError(output)

        self.log.debug(output)
