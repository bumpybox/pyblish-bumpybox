import os

import pyblish.api
import ftrack
import nuke


@pyblish.api.log
class ValidateNukeRenderOutput(pyblish.api.Validator):
    """ Validates the output path for nuke renders """

    families = ['deadline.render']
    hosts = ['nuke']
    version = (0, 1, 0)
    label = 'Render Output'

    def get_path(self, instance):
        ftrack_data = instance.context.data('ftrackData')
        shot_name = ftrack_data['Shot']['name']
        project = ftrack.Project(id=ftrack_data['Project']['id'])
        root = project.getRoot()
        file_name = os.path.basename(instance.context.data('currentFile'))
        file_name = os.path.splitext(file_name)[0]
        publish_output = os.path.join(root, 'renders', 'img_sequences',
                                      shot_name,
                                      file_name,
                                      str(instance))

        return publish_output

    def process(self, instance):

        # on going project specific exception
        ftrack_data = instance.context.data('ftrackData')
        if ftrack_data['Project']['code'] == 'the_call_up':
            return

        output = self.get_path(instance).replace('\\', '/')
        path = instance.data('deadlineJobData')['OutputFilename0']
        if os.path.dirname(path) != output:
            msg = 'Output path is incorrect on: %s' % str(instance)
            raise ValueError(msg)

    def repair(self, instance):
        node = nuke.toNode(str(instance))

        file_name = os.path.basename(node['file'].value())
        output = os.path.join(self.get_path(instance), file_name)
        node['file'].setValue(output.replace('\\', '/'))
