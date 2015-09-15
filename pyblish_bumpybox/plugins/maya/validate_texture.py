import os
import shutil

import pymel
import pyblish.api


class ValidateTexture(pyblish.api.Validator):
    """
    """

    families = ['texture']
    label = 'Texture'

    def expected_path(self, instance, context):

        node = instance[0]
        src = node.fileTextureName.get()

        current_dir = os.path.dirname(context.data('currentFile'))

        dst = os.path.join(current_dir, 'maps', os.path.basename(src))
        return dst.replace('\\', '/')

    def process(self, instance, context):

        node = instance[0]
        src = node.fileTextureName.get()
        dst = self.expected_path(instance, context)

        msg = 'Current path: %s\n\nExpected path: %s' % (src, dst)
        assert src == dst, msg

    def repair(self, instance, context):

        node = instance[0]
        src = node.fileTextureName.get()
        dst = self.expected_path(instance, context)

        if not os.path.exists(os.path.dirname(dst)):
            os.makedirs(os.path.dirname(dst))

        shutil.copy(src, dst)

        node.fileTextureName.set(dst)
