import os

import pyblish.api


class ValidateFFMPEG(pyblish.api.InstancePlugin):
    """Validates FFMPEG is available."""

    order = pyblish.api.ValidatorOrder
    optional = True
    label = "FFMPEG"
    families = ["mov", "img"]

    def process(self, instance):

        assert self.check_executable("ffmpeg"), "\"ffmpeg\" was not found."

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
                path = path.strip("\"")
                exe_file = os.path.join(path, executable)
                if is_exe(exe_file):
                    return True
                if is_exe(exe_file + ".exe"):
                    return True

        return False
