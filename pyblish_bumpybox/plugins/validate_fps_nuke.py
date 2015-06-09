import os

import nuke
import pyblish.api
import ftrack


@pyblish.api.log
class ValidateFPSNuke(pyblish.api.Validator):
    """ Validates the fps """

    families = ['scene']
    hosts = ['nuke']
    version = (0, 1, 0)
    optional = True

    def process(self, instance):

        # skipping the call up project
        ftrack_data = instance.context.data('ftrackData')
        if ftrack_data['Project']['code'] == 'the_call_up':
            return

        task = ftrack.Task(ftrack_data['Task']['id'])
        project = task.getParents()[-1]

        # validating fps
        local_fps = nuke.root()['fps'].value()

        online_fps = project.get('fps')

        msg = 'FPS is incorrect.'
        msg += '\n\nLocal fps: %s' % local_fps
        msg += '\n\nOnline fps: %s' % online_fps
        assert local_fps == online_fps, msg
