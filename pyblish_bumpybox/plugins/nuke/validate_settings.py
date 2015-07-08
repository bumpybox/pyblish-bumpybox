import os

import nuke
import pyblish.api
import ftrack


@pyblish.api.log
class ValidateSettings(pyblish.api.Validator):
    """ Validates settings """

    families = ['scene']
    hosts = ['nuke']
    version = (0, 1, 0)
    optional = True
    label = 'Settings'

    def process(self, instance):

        # skipping the call up project
        ftrack_data = instance.context.data('ftrackData')
        if ftrack_data['Project']['code'] == 'the_call_up':
            return

        task = ftrack.Task(ftrack_data['Task']['id'])
        project = task.getParents()[-1]
        shot = task.getParent()

        # validating fps
        local_fps = nuke.root()['fps'].value()

        online_fps = project.get('fps')

        msg = 'FPS is incorrect.'
        msg += '\n\nLocal fps: %s' % local_fps
        msg += '\n\nOnline fps: %s' % online_fps
        assert local_fps == online_fps, msg

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

        # validating resolution width
        local_width = nuke.root().format().width()

        online_width = int(project.get('resolution_width'))

        msg = 'Width is incorrect.'
        msg += '\n\nLocal width: %s' % local_width
        msg += '\n\nOnline width: %s' % online_width
        assert local_width == online_width, msg

        # validating resolution width
        local_height = nuke.root().format().height()

        online_height = int(project.get('resolution_height'))

        msg = 'Height is incorrect.'
        msg += '\n\nLocal height: %s' % local_height
        msg += '\n\nOnline height: %s' % online_height
        assert local_height == online_height, msg

    def repair(self, instance):

        # skipping the call up project
        ftrack_data = instance.context.data('ftrackData')
        if ftrack_data['Project']['code'] == 'the_call_up':
            return

        task = ftrack.Task(ftrack_data['Task']['id'])
        project = task.getParents()[-1]
        shot = task.getParent()

        nuke.root()['fps'].setValue(project.get('fps'))
        nuke.root()['first_frame'].setValue(shot.getFrameStart())
        nuke.root()['last_frame'].setValue(shot.getFrameEnd())

        width = int(project.get('resolution_width'))
        height = int(project.get('resolution_height'))
        name = project.getName()
        format_cmd = '%s %s 1.0 %s' % (width, height, name)
        new_format = nuke.addFormat(format_cmd)
        nuke.Root()['format'].setValue(new_format)
