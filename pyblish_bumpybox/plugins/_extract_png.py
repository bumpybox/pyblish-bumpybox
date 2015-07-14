import os
import shutil

import pyblish.api
import ftrack
import pyseq


@pyblish.api.log
class ExtractPNG(pyblish.api.Validator):
    """
    """

    families = ['png']

    def get_path(self, instance):
        ftrack_data = instance.context.data('ftrackData')
        shot_name = ftrack_data['Shot']['name']
        project = ftrack.Project(id=ftrack_data['Project']['id'])
        root = project.getRoot()
        file_name = os.path.basename(instance.data('currentFile'))
        file_name = os.path.splitext(file_name)[0]
        task_name = ftrack_data['Task']['name'].replace(' ', '_').lower()
        version_number = instance.context.data('version')
        version_name = 'v%s' % (str(version_number).zfill(3))
        filename = '.'.join([shot_name, task_name, version_name, str(instance),
                            '%04d'])

        output = os.path.join(root, 'renders', 'img_sequences', shot_name,
                                task_name, version_name, str(instance),
                                filename)

        return output

    def process(self, instance):

        seq = pyseq.uncompress(instance.data('path'))
        for f in seq:
            self.log.info(f)

        assert False, 'stop'
