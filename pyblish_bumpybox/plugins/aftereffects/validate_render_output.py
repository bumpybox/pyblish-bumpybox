import os

import pyblish.api


class ValidateRenderOutput(pyblish.api.Validator):
    """Validates the existence of version number on the scene
    """

    families = ['render']
    label = 'Render'
    optional = True

    def process(self, instance, context):

        msg = 'Multiple comps with the same name in the render queue.'
        assert context.data('sameNamedRenders'), msg

        ext = os.path.splitext(instance.data('path'))[1]
        msg = 'Please use either PNGs or EXRs. Currently using "%s"' % ext
        assert ext in ['.exr', '.png'], msg
