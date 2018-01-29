from pyblish import api
from pyblish_bumpybox import inventory


class ValidateFFmpeg(api.ContextPlugin):
    """Validate FFMPEG is available.

    FFMPEG is being used in various plugins for image and video processing.
    """

    order = inventory.get_order(__file__, "ValidateFFmpeg")
    label = "FFMPEG"
    optional = True

    def get_executable(self, executable):
        import os

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

    def process(self, context):

        self.get_executable("ffmpeg")
