import os
import subprocess

import pyblish.api


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


class ExtractMovie(pyblish.api.InstancePlugin):
    """Extracts movie from image sequence.

    Offset to get images to transcode from.
    """

    order = pyblish.api.ExtractorOrder + 0.1
    label = "Movie"
    optional = True
    families = ["img"]

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
