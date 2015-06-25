import os

import pyblish.api
import ftrack
import nuke


@pyblish.api.log
class ValidateNukeRenderDirectory(pyblish.api.Validator):
    """ Validates the output path for nuke renders """

    families = ['deadline.render']
    hosts = ['nuke']
    version = (0, 1, 0)
    label = 'Render Directory'

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

        path = instance.data('deadlineJobData')['OutputFilename0']

        # get output path
        basename = os.path.basename(path)
        output = self.get_path(instance)
        output = os.path.join(output, os.path.splitext(basename)[0] + '.exr')
        output = output.replace('\\', '/')

        # validate path
        if path != output:
            msg = 'Output path is incorrect on: %s' % str(instance)
            raise ValueError(msg)

    def repair(self, instance):

        # repairing the path string
        node = nuke.toNode(str(instance))
        path = node['file'].value()
        basename = os.path.basename(path)
        output = self.get_path(instance)
        output = os.path.join(output, basename)
        output = output.replace('\\', '/')

        node['file'].setValue(output)

        # making directories
        if not os.path.exists(os.path.dirname(output)):
            os.makedirs(os.path.dirname(output))
