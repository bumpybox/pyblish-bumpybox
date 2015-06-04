import os

import nuke
import pyblish.api
import ftrack


@pyblish.api.log
class ValidateFrameRangeNuke(pyblish.api.Validator):
    """ Validates the path of the nuke script """

    families = ['scene']
    hosts = ['nuke']
    version = (0, 1, 0)
    optional = True

    def process_instance(self, instance):

        # skipping the call up project
        ftrack_data = instance.context.data('ftrackData')
        if ftrack_data['Project']['code'] == 'the_call_up':
            return

        task = ftrack.Task(ftrack_data['Task']['id'])
        shot = task.getParent()

        # validating first frame
        local_first_frame = nuke.root()['first_frame'].value()

        online_first_frame = shot.getFrameStart()

        msg = 'First frame is incorrect.'
        msg += '\n\nLocal last frame: %s' % local_first_frame
        msg += '\n\nOnline last frame: %s' % online_first_frame
        assert local_first_frame == online_first_frame, msg

        # validating last frame
        local_last_frame = nuke.root()['last_frame'].value()

        online_last_frame = shot.getFrameEnd()

        msg = 'Last frame is incorrect.'
        msg += '\n\nLocal last frame: %s' % local_last_frame
        msg += '\n\nOnline last frame: %s' % online_last_frame
        assert local_last_frame == online_last_frame, msg
