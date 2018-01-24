import pyblish.api


class CollectPlayblasts(pyblish.api.ContextPlugin):
    """ Collects all playblast instances.

    Collects all cameras in scene, and presents as playblast instances.
    """

    order = pyblish.api.CollectorOrder
    label = "Playblasts"
    hosts = ["maya"]
    targets = ["default", "process.local"]

    def process(self, context):
        import os

        import pymel.core
        from maya import cmds
        from maya import mel

        default_cameras = ["persp", "top", "front", "side"]
        instances = []
        for camera in pymel.core.ls(type="camera"):

            transform = camera.getTransform()

            # Skip default cameras
            if transform.name() in default_cameras:
                continue

            # Remove illegal disk characters
            name = transform.name().replace(":", "_")

            # Movie instance
            instance = pyblish.api.Instance(name)
            instance.add(camera)
            instance.data["families"] = ["mov", "playblast"]
            instance.data["family"] = "mov"
            label = "{0} - {1}".format(name, "playblast")
            instance.data["label"] = label

            # Adding/Checking publish attribute
            instance.data["publish"] = False
            if hasattr(transform, "publish"):
                attr = pymel.core.Attribute(transform.name() + ".publish")
                instance.data["publish"] = attr.get()
            else:
                pymel.core.addAttr(
                    transform,
                    longName="publish",
                    defaultValue=False,
                    attributeType="bool"
                )
                attr = pymel.core.Attribute(transform.name() + ".publish")
                pymel.core.setAttr(attr, channelBox=True)

            # Set output path
            filename = "{0}_{1}.mov".format(
                os.path.splitext(
                    os.path.basename(context.data["currentFile"])
                )[0],
                name
            )
            path = os.path.join(
                os.path.dirname(context.data["currentFile"]),
                "workspace", filename
            )
            instance.data["output_path"] = path

            def instance_toggled(instance, value):
                instance[0].getTransform().publish.unlock()
                instance[0].getTransform().publish.set(value)
                instance[0].getTransform().publish.lock()
            instance.data["instanceToggled"] = instance_toggled

            instances.append(instance)

            # Collect audio
            playback_slider = mel.eval('$tmpVar=$gPlayBackSlider')
            audio_name = cmds.timeControl(playback_slider, q=True, s=True)
            display_sounds = cmds.timeControl(
                playback_slider, q=True, displaySound=True
            )

            audio = []

            if audio_name:
                audio.append(pymel.core.PyNode(audio_name))

            if not audio_name and display_sounds:
                start_frame = int(pymel.core.playbackOptions(q=True, min=True))
                end_frame = float(pymel.core.playbackOptions(q=True, max=True))
                frame_range = range(int(start_frame), int(end_frame))

                for node in pymel.core.ls(type="audio"):
                    # Check if frame range and audio range intersections,
                    # for whether to include this audio node or not.
                    start_audio = node.offset.get()
                    end_audio = node.offset.get() + node.duration.get()
                    audio_range = range(int(start_audio), int(end_audio))

                    if bool(set(frame_range).intersection(audio_range)):
                        audio.append(node)

            instance.data["audio"] = audio

        context.data["instances"] = (
            context.data.get("instances", []) + instances
        )


class CollectPlayblastsProcess(pyblish.api.ContextPlugin):
    """Collect all local processing write instances."""

    order = CollectPlayblasts.order + 0.01
    label = "Playblasts Local"
    hosts = ["maya"]
    targets = ["process.local"]

    def process(self, context):

        for item in context.data["instances"]:
            # Skip any instances that is not valid.
            if "playblast" not in item.data.get("families", []):
                continue

            instance = context.create_instance(item.data["name"])
            for key, value in item.data.iteritems():
                instance.data[key] = value

            instance.data["families"] += ["local"]
            for node in item:
                instance.add(node)


class CollectPlayblastsPublish(pyblish.api.ContextPlugin):
    """Collect all local processing write instances."""

    order = CollectPlayblasts.order + 0.01
    label = "Playblasts Local"
    hosts = ["maya"]
    targets = ["default"]

    def process(self, context):
        import os

        for item in context.data["instances"]:
            # Skip any instances that is not valid.
            if "playblast" not in item.data.get("families", []):
                continue

            if not os.path.exists(item.data["output_path"]):
                continue

            instance = context.create_instance(item.data["name"])
            for key, value in item.data.iteritems():
                instance.data[key] = value

            instance.data["label"] = "{0} - {1}".format(
                instance.data["name"],
                os.path.basename(instance.data["output_path"])
            )

            instance.data["families"] += ["output"]

            for node in item:
                instance.add(node)
