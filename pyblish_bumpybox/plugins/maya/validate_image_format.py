import os

import pyblish.api


@pyblish.api.log
class ValidateImageFormat(pyblish.api.Validator):
    """ Validates settings """

    families = ['deadline.render']
    optional = True
    label = 'Image Format'

    def process(self, instance):

        # skipping the call up project
        try:
            ftrack_data = instance.context.data('ftrackData')
            if ftrack_data['Project']['code'] == 'the_call_up':
                return
        except:
            pass

        ext = os.path.splitext(instance.data('deadlineData')['job']['OutputFilename0'])[1]

        msg = 'Image format is incorrect. Needs to be either EXR or PNG'
        assert ext in ['.exr', '.png'], msg
