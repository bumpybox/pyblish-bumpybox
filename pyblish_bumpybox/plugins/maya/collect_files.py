from pyblish import api
from pyblish_bumpybox import inventory


class CollectFiles(api.ContextPlugin):
    """ Collects file nodes from the scene. """

    order = inventory.get_order(__file__, "CollectFiles")
    label = "Files"
    targets = ["process"]

    def process(self, context):
        import os

        import pymel

        for node in pymel.core.ls(type="file"):
            # Ignore referenced nodes.
            if node.isReferenced():
                continue

            # Ignore nodes without a valid file
            if not node.fileTextureName.get():
                continue
            if not os.path.exists(node.fileTextureName.get()):
                continue

            # Create instance
            name = node.name()
            instance = context.create_instance(name=name)
            instance.add(node)
            instance.data["families"] = ["local", "img_file", "file"]
            instance.data["family"] = "file"
            label = "{0} - {1}".format(name, "file")
            instance.data["label"] = label

            # Adding/Checking publish attribute
            instance.data["publish"] = True
            if hasattr(node, "publish"):
                attr = pymel.core.Attribute(node.name() + ".publish")
                instance.data["publish"] = attr.get()
            else:
                pymel.core.addAttr(
                    node,
                    longName="publish",
                    defaultValue=True,
                    attributeType="bool"
                )
                attr = pymel.core.Attribute(node.name() + ".publish")
                pymel.core.setAttr(attr, channelBox=True)

            def instance_toggled(instance, value):
                instance[0].publish.set(value)
            instance.data["instanceToggled"] = instance_toggled
