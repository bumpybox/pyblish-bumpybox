from pyblish import api
from pyblish_bumpybox import inventory


class CollectScene(api.ContextPlugin):

    order = inventory.get_order(__file__, "CollectScene")

    def process(self, context):
        import traceback

        import pyblish_aftereffects

        try:
            path = pyblish_aftereffects.send("return app.project.file.fsName")
            context.data["currentFile"] = path.replace("\\", "/")
        except:
            self.log.warning(traceback.format_exc())
