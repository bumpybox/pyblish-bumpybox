import traceback

import pyblish.api
import pyblish_aftereffects


class CollectSceneAE(pyblish.api.ContextPlugin):
    order = pyblish.api.CollectorOrder

    def process(self, context):

        try:
            path = pyblish_aftereffects.send("return app.project.file.fsName")
            path = path.replace("\n", "").replace("\\", "/")
            context.data["currentFile"] = path
        except:
            self.log.warning(traceback.format_exc())
