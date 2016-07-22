import os
import re

import pyblish.api


class CleanupRender(pyblish.api.InstancePlugin):
    """ Integrates image and cache output """

    families = ["img.*"]
    order = pyblish.api.IntegratorOrder

    def process(self, instance):

        job = instance.context.data("deadlineJob")
        scene_file = job.GetJobPluginInfoKeyValue("SceneFile")

        if os.path.splitext(scene_file)[1] not in [".ifd"]:
            return

        # deleting all matching source files
        directory = os.path.dirname(scene_file)
        ext = os.path.splitext(scene_file)[1]
        pattern = r"\.[0-9]+\."
        frame = re.findall(pattern, os.path.basename(scene_file))[-1]
        start_base = os.path.basename(scene_file).split(frame)[0]

        for f in os.listdir(directory):
            if f.startswith(start_base) and f.endswith(ext):
                path = os.path.join(directory, f)
                os.remove(path)
                self.log.info("Deleting source file: " + path)
