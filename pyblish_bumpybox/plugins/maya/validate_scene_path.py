import os
import re

import pyblish.api
import pymel


class ValidateScenePath(pyblish.api.Validator):
    """ Validates the path of the maya scene """

    families = ['scene']
    label = 'Scene Path'

    def get_path(self, instance):

        path = []
        filename = []

        # get ftrack data
        ftrack_data = instance.context.data('ftrackData')
        path.append(ftrack_data['Project']['root'])
        child_path = []
        parent = False
        parent_name = ftrack_data['Project']['name']

        try:
            name = ftrack_data['Asset_Build']['name'].replace(' ', '_').lower()
            path.append('library')
            asset_type = ftrack_data['Asset_Build']['type'].lower()
            path.append(asset_type)
            path.append(name)
            parent_name = name
        except:
            self.log.info('No asset build found.')

        try:
            name = ftrack_data['Episode']['name'].replace(' ', '_').lower()
            path.append('episodes')
            child_path.append(name)
            parent = True
            parent_name = name
        except:
            self.log.info('No episode found.')

        try:
            name = ftrack_data['Sequence']['name'].replace(' ', '_').lower()
            child_path.append(name)

            if not parent:
                path.append('sequences')

            parent = True
            parent_name = name
        except:
            self.log.info('No sequences found.')

        try:
            name = ftrack_data['Shot']['name'].replace(' ', '_').lower()
            child_path.append(name)

            if not parent:
                path.append('shots')
            parent_name = name
        except:
            self.log.info('No shot found.')

        path.extend(child_path)

        task_name = ftrack_data['Task']['name'].replace(' ', '_').lower()
        path.append(task_name)

        version = 1
        if instance.context.has_data('version'):
            version = instance.context.data('version')
        version_string = 'v%s' % str(version).zfill(3)

        filename.append(parent_name)
        filename.append(task_name)
        filename.append(version_string)
        filename.append('mb')
        path.append('.'.join(filename))

        return os.path.join(*path).replace('\\', '/')

    def process(self, instance):

        # skipping the call up project
        ftrack_data = instance.context.data('ftrackData')
        if ftrack_data['Project']['code'] == 'the_call_up':
            return

        # validating scene work path
        file_path = self.get_path(instance)
        work_path = instance.data('workPath').replace('\\', '/')
        msg = 'Scene path is not correct:'
        msg += '\n\nCurrent: %s' % work_path
        msg += '\n\nExpected: %s' % file_path
        assert file_path == work_path, msg

    def repair(self, instance):
        """ Saves the maya scene to the correct path.
        """
        # saving nuke script
        file_path = self.get_path(instance)
        file_dir = os.path.dirname(file_path)

        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        pymel.core.system.saveAs(file_path)
