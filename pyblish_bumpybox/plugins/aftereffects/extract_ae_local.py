import os
import subprocess
import re

import pyblish.api
import pyblish_aftereffects


class ExtractAELocal(pyblish.api.InstancePlugin):
    """ Renders all publishable items locally. """

    order = pyblish.api.ExtractorOrder
    families = ["img.local.*"]
    label = "Render Local"

    def process(self, instance):

        # ensureing project on disk is updated
        pyblish_aftereffects.send("app.project.save()")

        # ensuring overwritting is enabled
        cmd = 'app.project.renderQueue.item({0}).setSettings'
        cmd += '({{"Skip Existing Files":true}})'
        pyblish_aftereffects.send(cmd.format(instance.data["index"]))

        # ensure output directory exists
        path = os.path.dirname(instance.data["output"])
        if not os.path.exists(path):
            os.makedirs(path)

        # launch aerender and execute rendering
        cmd = 'return BridgeTalk.getAppPath("aftereffects")'
        app_path = pyblish_aftereffects.send(cmd)
        render_exe = os.path.join(os.path.dirname(app_path), "aerender.exe")

        args = [render_exe, "-comp", instance.data["name"], "-project",
                instance.context.data["currentFile"]]

        result = subprocess.check_output(args)

        assert "ERROR:" not in result, result

        # adding output files to instance
        pattern = os.path.basename(instance.data["output"])
        pattern = pattern.replace(".[####].", r"\.[0-9]{4,}\.")
        self.log.debug("Pattern generated: " + pattern)

        files = []
        current_dir = os.path.dirname(instance.data["output"])
        for f in os.listdir(current_dir):
            if re.match(pattern, f):
                files.append(os.path.join(current_dir, f))

        instance.data["outputFiles"] = files
        self.log.debug("Extracted files: " + str(files))

        path = instance.data["output"].replace("[####]", "%04d")
        instance.data["outputPath"] = path
        self.log.debug("Output path: " + path)
