import os

import pyblish_aftereffects
import pyblish.api
import pipeline_schema


class RepairAEScenePathAction(pyblish.api.Action):
    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):

        # expected path
        data = pipeline_schema.get_data()
        data["extension"] = "aep"

        version = 1
        if context.has_data("version"):
            version = context.data("version")
        data["version"] = version

        file_path = pipeline_schema.get_path("task_work", data)

        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))

        cmd = "app.project.save(File(\"{0}\"))".format(file_path)
        pyblish_aftereffects.send(cmd)


class ValidateAEScenePath(pyblish.api.InstancePlugin):
    """ Validates the path of the hiero file """
    order = pyblish.api.ValidatorOrder
    families = ["scene"]
    label = "Scene Path"
    actions = [RepairAEScenePathAction]

    def process(self, instance):

        # getting current work file
        work_path = instance.data["workPath"].lower()

        # expected path
        data = pipeline_schema.get_data()
        data["extension"] = "aep"

        version = 1
        if instance.context.has_data("version"):
            version = instance.context.data("version")
        data["version"] = version

        file_path = pipeline_schema.get_path("task_work", data)

        # validating scene work path
        msg = "Scene path is not correct:"
        msg += "\n\nCurrent: %s" % (work_path)
        msg += "\n\nExpected: %s" % (file_path)

        assert file_path == work_path, msg
