import os

import hiero
import pyblish.api
import ftrack


@pyblish.api.log
class ValidateResolution(pyblish.api.Validator):
    """ Validates the resolution to ftrack """

    families = ['sequence']
    label = 'Settings'

    def process(self, instance, context):

        seq = instance[0]
        seq_format = seq.format()
        seq_framerate = seq.framerate()

        project = ftrack.Project(context.data('ftrackData')['Project']['id'])
        project_width = int(project.get('resolution_width'))
        project_height = int(project.get('resolution_height'))

        check = True

        if project.get('fps') != seq.framerate():
            msg = 'Framerate "%s" ' % seq.framerate()
            msg += 'was expected to be "%s"' % project.get('fps')
            self.log.error(msg)
            check = False

        if seq_format.width() != project_width:
            msg = 'Width "%s" ' % seq_format.width()
            msg += 'was expected to be "%s"' % project_width
            self.log.error(msg)
            check = False

        if seq_format.height() != project_height:
            msg = 'Height "%s" ' % seq_format.height()
            msg += 'was expected to be "%s"' % project_height
            self.log.error(msg)
            check = False

        assert check, 'Sequence "%s" settings are not correct.' % seq.name()
