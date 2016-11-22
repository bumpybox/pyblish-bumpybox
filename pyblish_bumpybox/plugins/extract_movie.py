import os
import subprocess

import pyblish.api


class BumpyboxExtractMovie(pyblish.api.InstancePlugin):
    """ Extracts movie from image sequence. """

    families = ["img"]
    order = pyblish.api.ExtractorOrder + 0.1
    label = "Movie"
    optional = True

    def process(self, instance):

        if not self.check_executable("ffmpeg"):
            msg = "Skipping movie extraction because \"ffmpeg\" wasn't found."
            self.log.info(msg)
            return

        collection = instance.data["collection"]

        if not list(collection):
            msg = "Skipping \"{0}\" because no frames was found."
            self.log.info(msg.format(instance.data["name"]))
            return

        if len(list(collection)) == 1:
            msg = "Skipping \"{0}\" because only a single frame was found."
            self.log.info(msg.format(instance.data["name"]))
            return

        args = ["ffmpeg", "-y", "-gamma", "2.2", "-framerate", "25",
                "-start_number", str(list(collection.indexes)[0]),
                "-i", collection.format("{head}{padding}{tail}"),
                "-q:v", "0", "-pix_fmt", "yuv420p", "-vf",
                "scale=trunc(iw/2)*2:trunc(ih/2)*2,colormatrix=bt601:bt709",
                "-timecode", "00:00:00:01",
                collection.format("{head}mov")]

        self.log.info("Executing args: {0}".format(args))

        process = subprocess.Popen(args, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        process.wait()
        output, error = process.communicate()

        if process.returncode:
            raise ValueError(error)

    def check_executable(self, executable):
        """ Checks to see if an executable is available.

        Args:
            executable (str): The name of executable without extension.

        Returns:
            bool: True for executable existance, False for non-existance.
        """

        def is_exe(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

        fpath, fname = os.path.split(executable)
        if fpath:
            if is_exe(executable):
                return True
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, executable)
                if is_exe(exe_file):
                    return True
                if is_exe(exe_file + ".exe"):
                    return True

        return False
