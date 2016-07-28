import os
import shutil

import pyblish.api
import pyblish_standalone
from pyblish_bumpybox.plugins import utils
import pipeline_schema


class RepairScenePath(pyblish.api.Action):
    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):

        # get version data
        version = 1
        if context.has_data('version'):
            version = context.data('version')

        # expected path
        data = pipeline_schema.get_data()
        data['version'] = version
        data['extension'] = 'scn'
        expected_path = pipeline_schema.get_path('task_work', data)

        # saving scene, if current directory is the same as the expected its
        # safe to assume to overwrite scene file
        current = context.data["currentFile"].replace("\\", "/")
        file_path = expected_path
        if os.path.dirname(expected_path) != os.path.dirname(current):
            file_path = utils.next_nonexisting_version(expected_path)

        file_dir = os.path.dirname(file_path)

        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        src = pyblish_standalone.kwargs['path'][0]

        shutil.copy(src, file_path)

        pyblish_standalone.kwargs['path'] = [file_path]

        self.log.info("Saved to \"%s\"" % file_path)


class ValidateScenePath(pyblish.api.InstancePlugin):
    """ Validates the path of the hiero file """
    order = pyblish.api.ValidatorOrder
    families = ['scene']
    label = 'Scene Path'
    actions = [RepairScenePath]

    def get_path(self, instance):

        path = []
        filename = []

        # get ftrack data
        ftrack_data = instance.context.data('ftrackData')
        path.append(ftrack_data['Project']['root'])

        try:
            ep_name = ftrack_data['Episode']['name'].replace(' ', '_').lower()
            path.append('episodes')
            path.append(ep_name)
        except:
            self.log.info('No episodes found.')

        try:
            seq_name = ftrack_data['Sequence']['name']
            seq_name = seq_name.replace(' ', '_').lower()
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
        filename.append('scn')

        path.append('.'.join(filename))
        path = os.path.join(*path).replace('\\', '/')

        return path

    def process(self, instance):

        # getting current work file
        work_path = pyblish_standalone.kwargs['path'][0].replace('\\', '/')
        work_path = work_path.lower()

        # get version data
        version = 1
        if instance.context.has_data('version'):
            version = instance.context.data('version')

        # expected path
        data = pipeline_schema.get_data()
        data['version'] = version
        data['extension'] = 'scn'
        file_path = pipeline_schema.get_path('task_work', data)
        """
        # if the path is completely invalid,
        # we need to find the next non-existing version to validate
        if file_path.split('v')[0] != work_path.split('v')[0]:
            self.log.info("Invalid path found.")
            file_path = utils.next_nonexisting_version(file_path)
        """

        # validating scene work path
        msg = 'Scene path is not correct:'
        msg += '\n\nCurrent: %s' % (work_path)
        msg += '\n\nExpected: %s' % (file_path)

        assert file_path == work_path, msg
