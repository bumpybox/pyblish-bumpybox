import pyblish.api


class ViewPlayblastsAction(pyblish.api.Action):

    label = "View Playblasts"
    icon = "eye"
    on = "all"

    def process(self, context, plugin):
        import os
        import webbrowser

        # Get the errored instances
        all_instances = []
        for result in context.data["results"]:
            all_instances.append(result["instance"])

        # Apply pyblish.logic to get the instances for the plug-in
        instances = pyblish.api.instances_by_plugin(context, plugin)

        for instance in instances:

            if not os.path.exists(instance.data["output_path"]):
                continue

            webbrowser.open(instance.data["output_path"])


class ExtractPlayblast(pyblish.api.InstancePlugin):
    """Extracts playblast."""

    order = pyblish.api.ExtractorOrder
    families = ["playblast"]
    optional = True
    label = "Playblast"
    hosts = ["maya"]
    targets = ["process.local"]
    actions = [ViewPlayblastsAction]

    def process(self, instance):
        import tempfile
        import subprocess
        import shutil
        import os

        from pyblish_bumpybox.capture import capture

        import pymel.core

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
            viewport_options={
                "rendererName": "vp2Renderer", "motionTrails": False
            },
            viewport2_options={
                "multiSampleEnable": True, "multiSampleCount": 8
            },
            camera_options={"panZoomEnabled": False},
        )

        movie_path = os.path.join(temp_dir, "temp.mov")

        # Copy font file to movie path
        shutil.copy(
            os.path.join(os.path.dirname(__file__), "arial.ttf"),
            os.path.join(os.path.dirname(movie_path), "arial.ttf")
        )

        # Using mpeg4 instead of h264 because Adobe Premiere can't read h264
        # correctly.
        start_frame = pymel.core.playbackOptions(q=True, min=True)
        args = [
            "ffmpeg", "-y",
            "-start_number", str(int(start_frame)),
            "-framerate", str(instance.context.data["framerate"]),
            "-i", os.path.join(temp_dir, "temp.%04d.jpg"),
        ]

        for node in instance.data["audio"]:
            offset_frames = start_frame - node.offset.get()
            offset_seconds = offset_frames / instance.context.data["framerate"]

            if offset_seconds > 0:
                args.append("-ss")
            else:
                args.append("-itsoffset")

            args.append(str(abs(offset_seconds)))

            args.extend(["-i", node.filename.get()])

        # Need to merge audio if there are more than 1 input.
        if len(instance.data["audio"]) > 1:
            args.extend(["-filter_complex", "amerge", "-ac", "2"])

        end_frame = pymel.core.playbackOptions(q=True, max=True)
        duration_frames = end_frame - start_frame + 1.0
        duration_seconds = duration_frames / instance.context.data["framerate"]
        args.extend([
            "-pix_fmt", "yuv420p",
            "-q:v", "1",
            "-c:v", "mpeg4",
            "-timecode", "00:00:00:01",
            "-t", str(duration_seconds),
            "-vf", "drawtext=fontfile=arial.ttf: text='Frame\\: %{n}':"
            " x=(w-tw) - lh: y=h-(2*lh): fontcolor=white: box=1:"
            " boxcolor=black@0.5: start_number=" + str(start_frame) + ": "
            "fontsize=32: boxborderw=5",
            movie_path
        ])

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
        if not os.path.exists(os.path.dirname(instance.data["output_path"])):
            os.makedirs(os.path.dirname(instance.data["output_path"]))
        shutil.copy(movie_path, instance.data["output_path"])

        # Clean up temporary files
        shutil.rmtree(temp_dir)
