from pyblish_bumpybox import plugin


class RepairScenePathAction(plugin.Action):
    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):
        import os

        import pipeline_schema
        import pyblish_aftereffects

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


class ValidateScenePath(plugin.InstancePlugin):
    """ Validates the path of the hiero file """
    order = plugin.ValidatorOrder
    families = ["scene"]
    label = "Scene Path"
    actions = [RepairScenePathAction]

    def process(self, instance):
        import pipeline_schema

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
