import traceback

import pyblish.api
import pyblish_aftereffects


class CollectAEScene(pyblish.api.ContextPlugin):

    order = pyblish.api.CollectorOrder

    def process(self, context):
        try:
            path = pyblish_aftereffects.send("return app.project.file.fsName")
            context.data["currentFile"] = path.replace("\\", "/")
        except:
            self.log.warning(traceback.format_exc())
