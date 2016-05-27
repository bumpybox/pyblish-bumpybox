import os

import hiero
import pyblish.api
import pipeline_schema


class RepairScenePath(pyblish.api.Action):

    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context):

        # get version data
        version = 1
        if context.has_data('version'):
            version = context.data('version')

        # expected path
        data = pipeline_schema.get_data()
        data['version'] = version
        data['extension'] = 'hrox'
        expected_path = pipeline_schema.get_path('task_work', data)

        # create folders if they don't exist
        file_dir = os.path.dirname(expected_path)
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        project = hiero.activeProject
        project.saveAs(expected_path)


class ValidateScenePath(pyblish.api.Validator):
    """ Validates the path of the hiero file """

    families = ['scene']
    label = 'Scene Path'
    actions = [RepairScenePath]

    def process(self, instance):

        # get version data
        version = 1
        if instance.context.has_data('version'):
            version = instance.context.data('version')

        # expected path
        data = pipeline_schema.get_data()
        data['version'] = version
        data['extension'] = 'hrox'
        expected_path = pipeline_schema.get_path('task_work', data)

        # validating scene work path
        current_path = instance.data('workPath').replace('\\', '/').lower()

        msg = 'Scene path is not correct:'
        msg += '\n\nCurrent: %s' % current_path
        msg += '\n\nExpected: %s' % expected_path
        assert current_path == expected_path, msg
