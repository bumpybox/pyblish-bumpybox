import pyblish.api


class CollectScene(pyblish.api.ContextPlugin):

    order = pyblish.api.CollectorOrder

    def process(self, context):
        import traceback

        import pyblish_aftereffects

        try:
            path = pyblish_aftereffects.send("return app.project.file.fsName")
            context.data["currentFile"] = path.replace("\\", "/")
        except:
            self.log.warning(traceback.format_exc())
