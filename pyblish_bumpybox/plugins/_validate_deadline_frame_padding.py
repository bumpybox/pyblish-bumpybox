import pyblish.api

@pyblish.api.log
class ValidateDeadlineFramePadding(pyblish.api.Validator):
    """ Validates the existence of four digit frame padding
    ('%04d or ####') in output.
    """

    families = ['deadline.render']
    label = 'Frame Padding'
    optional = True

    def process(self, instance):

        try:
            # skipping the call up project
            ftrack_data = instance.context.data('ftrackData')
            if ftrack_data['Project']['code'] == 'the_call_up':
                return
        except:
            pass

        if '-' in instance.data('deadlineFrames'):
            path = instance.data('deadlineData')['job']['OutputFilename0']
            msg = "Couldn't find any frame padding string ('%04d or ####')"
            msg += " in output on %s" % instance
            assert '####' in path or '%04d' in path, msg
