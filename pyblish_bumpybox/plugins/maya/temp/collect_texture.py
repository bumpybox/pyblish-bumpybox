import os

import pyblish.api
import pymel


class CollectTexture(pyblish.api.Collector):
    """
    """

    def process(self, context):

        for node in pymel.core.ls(type='file'):
            if node.isReferenced():
                continue

            if not node.fileTextureName.get():
                continue

            if not os.path.exists(node.fileTextureName.get()):
                continue

            name = os.path.basename(node.fileTextureName.get())
            instance = context.create_instance(name=name)
            instance.set_data('family', value='texture')
            instance.add(node)
            instance.data["publish"] = True

            try:
                attr = getattr(node, "pyblish_texture")
                instance.data["publish"] = attr.get()
            except:
                msg = "Attribute \"{0}\"".format("pyblish_texture")
                msg += " does not exists on: \"{0}\".".format(node.name())
                msg += " Defaulting to active publish"
                self.log.info(msg)
