import os
import shutil
import subprocess

import pyblish.api
import ftrack


class ValidateScenePath(pyblish.api.Validator):
    """ Validates the path of the hiero file """

    families = ['scene']
    label = 'Scene Path'

    def get_path(self, instance):

        path = []
        filename = []

        # get ftrack data
        ftrack_data = instance.context.data('ftrackData')
        project = ftrack.Project(id=ftrack_data['Project']['id'])
        path.append(ftrack_data['Project']['root'])

        try:
            ep_name = ftrack_data['Episode']['name'].replace(' ', '_').lower()
            path.append('episodes')
            path.append(ep_name)
        except:
            self.log.info('No episodes found.')

        try:
            seq_name = ftrack_data['Sequence']['name'].replace(' ', '_').lower()
            if 'Episode' not in ftrack_data:
                path.append('sequences')
            path.append(seq_name)
        except:
            self.log.info('No sequences found.')

        try:
            shot_name = ftrack_data['Shot']['name'].replace(' ', '_').lower()
            path.append(shot_name)
            filename.append(shot_name)
        except:
            self.log.info('No shot found.')

        task_name = ftrack_data['Task']['name'].replace(' ', '_').lower()
        path.append(task_name)
        filename.append(task_name)

        # get version data
        version = 1
        if instance.context.has_data('version'):
            version = instance.context.data('version')
        version_string = 'v%s' % str(version).zfill(3)

        filename.append(version_string)

        path.append('.'.join(filename))

        return os.path.join(*path).replace('\\', '/')

    def process(self, instance):

        # validating scene work path
        file_path = self.get_path(instance)

        basename = os.path.basename(instance.data('workPath'))
        if ('_') in basename:
            basename = basename.split('_')[0]
        else:
            basename = os.path.splitext(basename)[0]

        path = os.path.dirname(instance.data('workPath'))
        work_path = os.path.join(path, basename).replace('\\','/')

        msg = 'Scene path is not correct:'
        msg += '\n\nCurrent start with: %s' % (work_path + '.scn')
        msg += '\n\nExpected start with: %s' % (file_path + '.scn')
        assert file_path == work_path, msg

    def repair(self, instance):

        # saving scene
        file_path = self.get_path(instance)
        file_dir = os.path.dirname(file_path)

        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        src = instance.data('workPath').replace('\\','/')
        dst = file_path + '.scn'

        shutil.copy(src, dst)

        import webbrowser
        webbrowser.open('file://%s' % file_dir)
