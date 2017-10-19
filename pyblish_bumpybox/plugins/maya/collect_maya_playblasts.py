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
    targets = ["default", "process.local"]

    def process(self, context):

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
                instance[0].getTransform().publish.set(value)
            instance.data["instanceToggled"] = instance_toggled

            instances.append(instance)

        context.data["instances"] = (
            context.data.get("instances", []) + instances
        )


class CollectMayaPlayblastsLocal(pyblish.api.ContextPlugin):
    """Collect all local processing write instances."""

    order = CollectMayaPlayblasts.order + 0.01
    label = "Playblasts Local"
    hosts = ["maya"]
    targets = ["process.local"]

    def process(self, context):

        for item in context.data["instances"]:
            # Skip any instances that is not valid.
            valid_families = ["playblasts"]
            if len(set(valid_families) & set(item.data["families"])) != 1:
                continue

            instance = context.create_instance(item.data["name"])
            for key, value in item.data.iteritems():
                instance.data[key] = value

            instance.data["families"] += ["local"]
            for node in item:
                instance.add(node)
