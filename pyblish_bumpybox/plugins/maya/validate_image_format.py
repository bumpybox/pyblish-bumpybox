import os

import pymel
import pyblish.api
import ftrack


@pyblish.api.log
class ValidateImageFormat(pyblish.api.Validator):
    """ Validates settings """

    families = ['deadline.render']
    optional = True
    label = 'Image Format'

    def process(self, instance):

        # skipping the call up project
        ftrack_data = instance.context.data('ftrackData')
        if ftrack_data['Project']['code'] == 'the_call_up':
            return

        img = pymel.core.rendering.renderSettings(firstImageName=True)[0]
        ext = os.path.splitext(img)[1]

        msg = 'Image format is incorrect. Needs to be either EXR or PNG'
        assert ext in ['.exr', '.png'], msg
