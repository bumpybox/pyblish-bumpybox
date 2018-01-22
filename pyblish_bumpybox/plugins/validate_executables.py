import os

import pyblish.api


class ValidateFFmpeg(pyblish.api.ContextPlugin):
    """Validate FFMPEG is available.

    FFMPEG is being used in various plugins for image and video processing.
    """

    order = pyblish.api.ValidatorOrder
    label = "FFMPEG"
    optional = True

    def get_executable(self, executable):

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

    def process(self, instance):

        self.get_executable("ffmpeg")
