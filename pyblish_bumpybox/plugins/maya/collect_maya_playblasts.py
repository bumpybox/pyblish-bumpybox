import os

import pyblish.api
import pymel.core


class CollectMayaPlayblasts(pyblish.api.ContextPlugin):
    """ Collects all playblast instances.

    Collects all cameras in scene, and presents as playblast instances.
    """

    order = pyblish.api.CollectorOrder
    label = "Playblasts"
    hosts = ["maya"]

    def process(self, context):

        default_cameras = ["persp", "top", "front", "side"]
        for camera in pymel.core.ls(type="camera"):

            transform = camera.getTransform()

            # Skip default cameras
            if transform.name() in default_cameras:
                continue

            # Remove illegal disk characters
            name = transform.name().replace(":", "_")

            # Movie instance
            instance = context.create_instance(name=name)
            instance.add(camera)
            instance.data["families"] = ["local", "mov", "playblast"]
            instance.data["family"] = "mov"
            label = "{0} - {1} - {2}".format(name, "playblast", "local")
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
