import os
import re

import pyblish.api


class ExtractLocal(pyblish.api.InstancePlugin):
    """ Extracts "img" and "cache" locally """

    families = ["img.local.*", "cache.local.*"]
    order = pyblish.api.ExtractorOrder
    label = "Local"
    optional = True

    def process(self, instance):

        node = instance[0]

        node.parm("execute").pressButton()

        # raising any errors
        if node.errors():
            raise ValueError(node.errors())

        # gather extracted files
        output_path = instance.data["outputPath"]

        pattern = os.path.basename(output_path)
        pattern = pattern.replace(".%04d.", r"\.[0-9]{4}\.")
        self.log.debug("Pattern generated: " + pattern)

        files = []
        current_dir = os.path.dirname(output_path)
        for f in os.listdir(current_dir):
            if re.match(pattern, f):
                files.append(os.path.join(current_dir, f))

        instance.data["outputFiles"] = files
        self.log.debug("Extracted files: " + str(files))
