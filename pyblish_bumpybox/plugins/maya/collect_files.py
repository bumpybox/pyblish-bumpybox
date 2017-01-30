import os

import pyblish.api
import pymel


class BumpyboxMayaCollectFiles(pyblish.api.Collector):
    """ Collects file nodes from the scene. """

    def process(self, context):

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
            name = os.path.basename(node.fileTextureName.get())
            instance = context.create_instance(name=name)
            instance.add(node)
            instance.data["families"] = ["local", "img", "file"]
            label = "{0} - {1} - {2}".format(name, "file", "local")
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
