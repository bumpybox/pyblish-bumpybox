import os

import nuke
import pyblish.api
import ftrack


@pyblish.api.log
class ValidateScenePath(pyblish.api.Validator):
    """ Validates the path of the nuke script """

    families = ['scene']
    label = 'Scene Path'

    def get_path(self, instance):
        # get ftrack data
        ftrack_data = instance.context.data('ftrackData')
        project = ftrack.Project(id=ftrack_data['Project']['id'])
        root_dir = ftrack_data['Project']['root']
        task_name = ftrack_data['Task']['name']
        task_name = task_name.replace(' ', '_').lower()

        version = 1
        if instance.context.has_data('version'):
            version = instance.context.data('version')
        version_string = 'v%s' % str(version).zfill(3)

        file_path = ''
        if 'Sequence' in ftrack_data:
            seq_name = ftrack_data['Sequence']['name']
            shot_name = ftrack_data['Shot']['name'].replace(' ', '_')
            shot_name = shot_name.lower()
            file_name = '.'.join([shot_name, task_name,
                                 version_string, 'nk'])
            file_path = os.path.join(root_dir, 'sequences', seq_name, shot_name,
                                     task_name, file_name)
        else:
            asset_type = ftrack_data['Asset_Build']['type'].replace(' ', '_')
            asset_type = asset_type.lower()
            asset_name = ftrack_data['Asset_Build']['name'].replace(' ', '_')
            asset_name = asset_name.lower()
            file_name = '.'.join([asset_name, task_name,
                                 version_string, 'nk'])
            file_path = os.path.join(root_dir, 'library', asset_type,
                                    asset_name, task_name, file_name)

        return file_path

    def process(self, instance):

        # skipping the call up project
        ftrack_data = instance.context.data('ftrackData')
        if ftrack_data['Project']['code'] == 'the_call_up':
            return

        # validating scene work path
        file_path = self.get_path(instance)
        msg = 'Scene path is not correct:'
        msg += '\n\nCurrent: %s' % instance.data('workPath')
        msg += '\n\nExpected: %s' % file_path
        assert file_path == instance.data('workPath'), msg


    def repair(self, instance):
        """ Saves the nuke script to the correct path.
        """
        # saving nuke script
        file_path = self.get_path(instance)
        file_dir = os.path.dirname(file_path)

        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        nuke.scriptSaveAs(file_path)
