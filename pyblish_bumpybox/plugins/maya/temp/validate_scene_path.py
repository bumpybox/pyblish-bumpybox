import os

import pyblish.api
import pymel
import pipeline_schema


class RepairScenePath(pyblish.api.Action):

    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context):

        # get version data
        version = 1
        if context.has_data("version"):
            version = context.data("version")

        data = pipeline_schema.get_data()
        data["extension"] = "mb"
        data["version"] = version
        file_path = pipeline_schema.get_path("task_work", data)
        file_dir = os.path.dirname(file_path)

        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        pymel.core.system.saveAs(file_path)


class ValidateScenePath(pyblish.api.Validator):
    """ Validates the path of the maya scene """

    families = ['scene']
    label = 'Scene Path'
    actions = [RepairScenePath]

    def process(self, instance):

        # get version data
        version = 1
        if instance.context.has_data("version"):
            version = instance.context.data("version")

        # validating scene work path
        data = pipeline_schema.get_data()
        data["version"] = version
        data["extension"] = "mb"
        file_path = pipeline_schema.get_path("task_work", data)

        work_path = instance.data('workPath').replace('\\', '/').lower()

        msg = 'Scene path is not correct:'
        msg += ' Current: %s' % work_path
        msg += ' Expected: %s' % file_path
        assert file_path == work_path, msg
