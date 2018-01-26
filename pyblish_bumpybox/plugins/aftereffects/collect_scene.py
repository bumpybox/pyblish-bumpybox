from pyblish import api


class CollectScene(api.ContextPlugin):

    order = api.CollectorOrder

    def process(self, context):
        import traceback

        import pyblish_aftereffects

        try:
            path = pyblish_aftereffects.send("return app.project.file.fsName")
            context.data["currentFile"] = path.replace("\\", "/")
        except:
            self.log.warning(traceback.format_exc())
