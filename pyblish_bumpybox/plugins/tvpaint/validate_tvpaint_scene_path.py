import os
import subprocess

import pyblish.api
import ftrack


@pyblish.api.log
class ValidateTVPaintScenePath(pyblish.api.Validator):
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

        # extension
        ext = os.path.splitext(instance.context.data('currentFile'))[1]
        self.log.info(instance.context.data('currentFile'))
        try:
            filename.append(ext.split('.')[1])
        except:
            filename.append('hrox')

        path.append('.'.join(filename))

        return os.path.join(*path).replace('\\', '/')

    def process(self, instance):

        # validating scene work path
        file_path = self.get_path(instance)
        msg = 'Scene path is not correct:'
        msg += '\n\nCurrent: %s' % instance.data('workPath').replace('\\','/')
        msg += '\n\nExpected: %s' % file_path
        assert file_path == instance.data('workPath').replace('\\','/'), msg

    def repair(self, instance):
        """
        """
        # saving scene
        file_path = self.get_path(instance)
        file_dir = os.path.dirname(file_path)

        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        args = []
        cmd = r'C:\Program Files\TVPaint Developpement'
        cmd += r'\TVPaint Animation 11 Pro (64bits)'
        cmd += r'\TVPaint Animation 11 Pro (64bits).exe'
        args.append(cmd)
        args.append('cmd=[tv_SaveProject %s]' % file_path)

        subprocess.Popen(args)
