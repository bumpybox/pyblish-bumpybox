import os

import pyblish.api
import pyblish_aftereffects


class CollectAERenderItems(pyblish.api.ContextPlugin):
    """ Collect render queue items. """

    order = pyblish.api.CollectorOrder

    def process(self, context):

        cmd = "return app.project.renderQueue.numItems"
        itemCount = int(pyblish_aftereffects.send(cmd))
        for count in range(1, itemCount + 1):

            cmd = "return app.project.renderQueue.item({0}).comp.name"
            name = pyblish_aftereffects.send(cmd.format(count))

            cmd = "return app.project.renderQueue.item({0}).outputModule(1)"
            cmd += ".file.fsName"
            output = ""
            try:
                output = pyblish_aftereffects.send(cmd.format(count))
            except:
                pass

            ext = os.path.splitext(output)[1]

            # hardcoding frame padding to 4 for now, as output path
            # validation is rigid on padding
            frame_padding = 4

            instance = context.create_instance(name)
            instance.data["family"] = "img.farm" + ext
            instance.data["families"] = ["img.farm.*", "img.*", "deadline"]
            instance.data["output"] = output
            instance.data["index"] = count
            instance.data["framePadding"] = frame_padding

            instance = context.create_instance(name)
            instance.data["family"] = "img.local" + ext
            instance.data["families"] = ["img.local.*", "img.*"]
            instance.data["publish"] = False
            instance.data["output"] = output
            instance.data["index"] = count
            instance.data["framePadding"] = frame_padding
