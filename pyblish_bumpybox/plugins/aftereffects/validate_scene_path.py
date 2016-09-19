import pyblish.api

import pipeline_schema


class ValidateScenePath(pyblish.api.InstancePlugin):
    """ Validates the path of the after effects file """
    order = pyblish.api.ValidatorOrder
    families = ["scene"]
    label = "Scene Path"

    def process(self, instance):

        # getting current work file
        work_path = instance.data["workPath"]

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
