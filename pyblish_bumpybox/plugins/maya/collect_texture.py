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
