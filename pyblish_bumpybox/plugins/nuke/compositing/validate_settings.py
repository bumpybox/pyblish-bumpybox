import nuke
import pyblish.api
import ftrack


class RepairSettings(pyblish.api.Action):

    label = 'Repair'
    icon = 'wrench'
    on = 'failed'

    def process(self, context, plugin):

        ftrack_data = context.data('ftrackData')
        task = ftrack.Task(ftrack_data['Task']['id'])
        project = task.getParents()[-1]
        shot = task.getParent()

        nuke.root()['fps'].setValue(project.get('fps'))
        nuke.root()['first_frame'].setValue(shot.getFrameStart())

        handles = shot.get('handles')
        last_frame = shot.getFrameEnd() + (handles * 2)
        nuke.root()['last_frame'].setValue(last_frame)


class ValidateSettings(pyblish.api.Validator):
    """ Validates settings """

    families = ['scene']
    optional = True
    label = 'Settings'
    actions = [RepairSettings]

    def process(self, context):

        ftrack_data = context.data('ftrackData')

        # skipping asset builds
        if 'Asset_Build' in ftrack_data:
            return

        task = ftrack.Task(ftrack_data['Task']['id'])
        project = task.getParents()[-1]
        shot = task.getParent()

        handles = shot.get('handles')

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

        online_last_frame = shot.getFrameEnd() + (handles * 2)

        msg = 'Last frame is incorrect.'
        msg += '\n\nLocal last frame: %s' % local_last_frame
        msg += '\n\nOnline last frame: %s' % online_last_frame
        assert local_last_frame == online_last_frame, msg
