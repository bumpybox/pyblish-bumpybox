import os

import pyblish.api
import pyblish_aftereffects


class CollectRenderItems(pyblish.api.ContextPlugin):
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

            instance = context.create_instance(name)
            instance.data["family"] = "img.farm" + ext
            instance.data["families"] = ["img.farm.*", "img.*", "deadline"]
            instance.data["publish"] = False
            instance.data["output"] = output
            instance.data["index"] = count

            instance = context.create_instance(name)
            instance.data["family"] = "img.local" + ext
            instance.data["families"] = ["img.local.*", "img.*"]
            instance.data["output"] = output
            instance.data["index"] = count
            """
            cmd = "return app.project.renderQueue.item({0}).comp.frameDuration"
            frame_duration = pyblish_aftereffects.send(cmd.format(count))
            frame_duration = float(frame_duration)

            cmd = "return app.project.renderQueue.item({0}).timeSpanStart"
            time_start = float(pyblish_aftereffects.send(cmd.format(count)))
            first_frame = time_start * (1 / frame_duration)

            cmd = "return app.project.renderQueue.item({0}).timeSpanDuration"
            time_duration = float(pyblish_aftereffects.send(cmd.format(count)))
            last_frame = time_duration * (1 / frame_duration)

            self.log.info((name, output, first_frame, last_frame))
            """
