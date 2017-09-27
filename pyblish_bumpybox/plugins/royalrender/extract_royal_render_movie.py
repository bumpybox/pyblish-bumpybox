import os

import pyblish.api


class ExtractRoyalRenderMovie(pyblish.api.InstancePlugin):
    """Appending RoyalRender movie job data."""

    families = ["royalrender", "img"]
    order = pyblish.api.ExtractorOrder
    match = pyblish.api.Subset
    label = "Royal Render Movie"
    targets = ["process.royalrender"]

    def process(self, instance):

        collection = instance.data["collection"]

        # Start number needs to always be the first file of the existing
        # frames, in order to ensure the full movie gets exported.
        # This is to support patch rendering.
        root = os.path.dirname(collection.format())
        indexes = []
        for f in os.listdir(root):
            file_path = os.path.join(root, f).replace("\\", "/")
            match = collection.match(file_path)
            if match:
                indexes.append(int(match.groupdict()["index"]))

        # If no existing files are found, we assume its a new render and use
        # the collections indexes.
        if not indexes:
            indexes = collection.indexes

        data = (
            "\"{0}\" -y -gamma 2.2 -framerate {1} -start_number {2} -i \"{3}\""
            " -q:v 0 -pix_fmt yuv420p -vf scale=trunc(iw/2)*2:trunc(ih/2)*2,"
            "colormatrix=bt601:bt709 -timecode 00:00:00:01 \"{4}\"".format(
                self.get_executable_path("ffmpeg"),
                instance.context.data["framerate"],
                min(indexes),
                collection.format("{head}{padding}{tail}").replace("%", "%%"),
                collection.format("{head}.mov")
            )
        )
        file_path = collection.format("{head}.bat")
        with open(file_path, "w") as f:
            f.write(data)

        data = {
            "Software": "Execute",
            "SeqStart": 1,
            "SeqEnd": 1,
            "SeqStep": 1,
            "SeqFileOffset": 0,
            "Version": 1.0,
            "SceneName": file_path,
            "ImageDir": os.path.dirname(instance.data["collection"].format()),
            "ImageFilename": "execOnce.file",
            "ImageExtension": "",
            "ImagePreNumberLetter": ".",
            "ImageSingleOutputFile": "true",
            "SceneOS": "win",
            "Layer": "",
            "PreID": 1,
            "WaitForPreID": 0,
            "IsActive": True,
        }

        # Adding job
        jobs = instance.data.get("royalrenderJobs", [])
        jobs.append(data)
        instance.data["royalrenderJobs"] = jobs

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

        raise IOError("\"{0}\" executable not found.")
