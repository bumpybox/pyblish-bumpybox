import os

import pymel
import pyblish.api
import ftrack


@pyblish.api.log
class ValidateFrameRange(pyblish.api.Validator):
    """ Validates settings """

    families = ['deadline.render']
    optional = True
    label = 'Frame Range'

    def process(self, instance, context):

        # skipping the call up project
        ftrack_data = instance.context.data('ftrackData')
        if ftrack_data['Project']['code'] == 'the_call_up':
            return

        # validate frame range
        if 'Shot' in ftrack_data:
            task = ftrack.Task(ftrack_data['Task']['id'])
            project = task.getParents()[-1]
            shot = task.getParent()

            local_first_frame = render_globals.startFrame.get()

            online_first_frame = shot.getFrameStart()

            msg = 'First frame is incorrect.'
            msg += '\n\nLocal last frame: %s' % local_first_frame
            msg += '\n\nOnline last frame: %s' % online_first_frame
            assert local_first_frame == online_first_frame, msg

            local_last_frame = render_globals.endFrame.get()

            online_last_frame = shot.getFrameEnd()

            msg = 'Last frame is incorrect.'
            msg += '\n\nLocal last frame: %s' % local_last_frame
            msg += '\n\nOnline last frame: %s' % online_last_frame
            assert local_last_frame == online_last_frame, msg

    def repair(self, instance, context):

        # repairing frame range
        if 'Shot' in ftrack_data:
            task = ftrack.Task(ftrack_data['Task']['id'])
            project = task.getParents()[-1]
            shot = task.getParent()

            render_globals.startFrame.set(shot.getFrameStart())
            render_globals.endFrame.set(shot.getFrameEnd())
