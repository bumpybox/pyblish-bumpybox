import tempfile
import os
import subprocess
import shutil
import webbrowser

import pymel.core

import pyblish.api
from capture import capture


class ViewPlayblastAction(pyblish.api.Action):

    label = "View Playblast"
    icon = "eye"
    on = "succeeded"

    def process(self, context, plugin):

        # Get the errored instances
        succeeded = []
        for result in context.data["results"]:
            if (result["error"] is None and result["instance"] is not None
               and result["instance"] not in succeeded):
                succeeded.append(result["instance"])

        # Apply pyblish.logic to get the instances for the plug-in
        instances = pyblish.api.instances_by_plugin(succeeded, plugin)

        for instance in instances:
            webbrowser.open(instance.data["output_path"])


class ExtractMayaPlayblast(pyblish.api.InstancePlugin):
    """Extracts playblast."""

    order = pyblish.api.ExtractorOrder
    families = ["playblast"]
    optional = True
    label = "Playblast"
    hosts = ["maya"]
    targets = ["process.local"]
    actions = [ViewPlayblastAction]

    def process(self, instance):

        temp_dir = tempfile.mkdtemp()
        capture(
            instance[0].getTransform().name(),
            filename=os.path.join(temp_dir, "temp"),
            format="image",
            compression="jpg",
            viewer=False,
            show_ornaments=False,
            overwrite=True,
            off_screen=True,
            viewport_options={"rendererName": "vp2Renderer"},
            viewport2_options={
                "multiSampleEnable": True, "multiSampleCount": 8
            },
            camera_options={"panZoomEnabled": False},
        )

        movie_path = os.path.join(temp_dir, "temp.mov")
        args = [
            "ffmpeg", "-y",
            "-start_number", str(
                int(pymel.core.playbackOptions(q=True, min=True))
            ),
            "-framerate", str(instance.context.data["framerate"]),
            "-i", os.path.join(temp_dir, "temp.%04d.jpg"),
            "-pix_fmt", "yuv420p",
            "-crf", "18",
            "-timecode", "00:00:00:01",
            movie_path
        ]

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

        # Copy movie to final destination
        shutil.copy(movie_path, instance.data["output_path"])

        # Clean up temporary files
        shutil.rmtree(temp_dir)
