import os

import nuke
import pyblish.api
import ftrack


@pyblish.api.log
class ValidateResolutionNuke(pyblish.api.Validator):
    """ Validates the resolution """

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
        project = task.getParents()[-1]

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
