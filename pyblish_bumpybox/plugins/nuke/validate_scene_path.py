import os

import nuke
import pyblish.api
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

        # saving nuke script
        data = pipeline_schema.get_data()
        data["version"] = version
        data["extension"] = "nk"
        file_path = pipeline_schema.get_path("task_work", data)
        file_dir = os.path.dirname(file_path).lower()

        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        nuke.scriptSaveAs(file_path)


class ValidateScenePath(pyblish.api.Validator):
    """ Validates the path of the nuke script """

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
        data["extension"] = "nk"
        file_path = pipeline_schema.get_path("task_work", data)

        work_path = instance.data('workPath').replace('\\', '/')

        msg = 'Scene path is not correct:'
        msg += '\n\nCurrent: %s' % work_path
        msg += '\n\nExpected: %s' % file_path
        assert file_path.lower() == work_path.lower(), msg
