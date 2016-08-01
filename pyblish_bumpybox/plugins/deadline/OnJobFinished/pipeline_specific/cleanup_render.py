import os
import re

import pyblish.api


class CleanupRender(pyblish.api.InstancePlugin):
    """ Cleanup after renders """

    families = ["img.*"]
    order = pyblish.api.IntegratorOrder + 0.5

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


class CleanupMovie(pyblish.api.InstancePlugin):
    """ Cleanup after movies """

    families = ["mov.*"]
    order = pyblish.api.IntegratorOrder + 0.5

    def process(self, instance):

        job = instance.context.data("deadlineJob")
        input_files = job.GetJobPluginInfoKeyValue("InputFile0")
        input_files = input_files.replace("\\", "/")

        # deleting all matching source files
        directory = os.path.dirname(input_files)

        if not os.path.exists(directory):
            return

        pattern = input_files.replace(".%04d.", r"\.[0-9]{4}\.")
        self.log.info("Pattern generated: " + pattern)

        for f in os.listdir(directory):
            f = os.path.join(directory, f).replace("\\", "/")
            if re.match(pattern, f):
                os.remove(f)
                self.log.info("Deleting source file: " + f)

        f = job.GetJobPluginInfoKeyValue("OutputFile")
        os.remove(f)
        self.log.info("Deleting source file: " + f)
