from pyblish_bumpybox import plugin


class CollectScene(plugin.ContextPlugin):

    order = plugin.CollectorOrder

    def process(self, context):
        import traceback

        import pyblish_aftereffects

        try:
            path = pyblish_aftereffects.send("return app.project.file.fsName")
            context.data["currentFile"] = path.replace("\\", "/")
        except:
            self.log.warning(traceback.format_exc())
