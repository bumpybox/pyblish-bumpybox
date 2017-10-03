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


class ExtractViewerLut(pyblish.api.InstancePlugin):
    """Extract the Nuke viewer LUT"""

    order = pyblish.api.ExtractorOrder
    label = "Viewer LUT"
    families = ["img"]
    hosts = ["nuke"]

    def process(self, instance):
        import nuke

        # Deselect all nodes to prevent external connections
        [i["selected"].setValue(False) for i in nuke.allNodes()]

        # Create nodes
        viewer_process_node = nuke.ViewerProcess.node()
        cms_node = nuke.createNode("CMSTestPattern")
        dag_node = nuke.createNode(viewer_process_node.Class())
        generate_lut_node = nuke.createNode("GenerateLUT")

        # Copy viewer process values
        excludedKnobs = ["name", "xpos", "ypos"]
        for item in viewer_process_node.knobs().keys():
            if item not in excludedKnobs and item in dag_node.knobs():
                x1 = viewer_process_node[item]
                x2 = dag_node[item]
                x2.fromScript(x1.toScript(False))

        # Setup generate lut node
        collection = instance.data["collection"]
        output_path = collection.format("{head}.cube")
        generate_lut_node["file"].setValue(output_path.replace("\\", "/"))
        generate_lut_node["file_type"].setValue(6)

        # Extract LUT file
        nuke.execute(generate_lut_node, 0, 0)

        # Clean up nodes
        nuke.delete(cms_node)
        nuke.delete(dag_node)
        nuke.delete(generate_lut_node)


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
            self.log.warning(msg.format(instance.data["name"]))
            return

        collection = instance.data["collection"]

        # Start number needs to always be the first file of the existing
        # frames, in order to ensure the full movie gets exported.
        # Also finding any LUT file to use.
        root = os.path.dirname(collection.format())
        indexes = []
        lut_file = None
        for f in os.listdir(root):
            file_path = os.path.join(root, f).replace("\\", "/")
            match = collection.match(file_path)
            if match:
                indexes.append(int(match.groupdict()["index"]))

            if f.endswith(".cube"):
                lut_file = f

        # Generate args.
        # Has to be yuv420p for compatibility with older players and smooth
        # playback. This does come with a sacrifice of more visible banding
        # issues.
        args = [
            "ffmpeg", "-y",
            "-start_number", str(min(indexes)),
            "-framerate", str(instance.context.data["framerate"]),
            "-i", collection.format("{head}{padding}{tail}"),
            "-pix_fmt", "yuv420p",
            "-crf", "0",
            "-timecode", "00:00:00:01",
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

        if p.returncode != 0:
            raise ValueError(output)

        self.log.debug(output)
