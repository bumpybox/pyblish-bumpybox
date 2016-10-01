import os
import shutil
import re

import pyblish.api
import pipeline_schema


class IntegrateLocal(pyblish.api.InstancePlugin):
    """ Integrates local output """

    families = ["img.local.*", "cache.local.*"]
    label = "Local"
    order = pyblish.api.IntegratorOrder
    optional = True

    def process(self, instance):

        data = pipeline_schema.get_data()
        ext = os.path.splitext(instance.data["family"])[1].replace("_", ".")
        data["extension"] = ext[1:]
        data["output_type"] = "img"
        data["name"] = str(instance)

        if instance.data["family"].startswith("cache"):
            data["output_type"] = "cache"

        output_seq = pipeline_schema.get_path("output_sequence", data=data)
        output_file = pipeline_schema.get_path("output_file", data=data)

        # move output
        pattern = r"\.[0-9]{4,}\."
        for f in instance.data["outputFiles"]:
            dst = output_file

            parent_dir = os.path.dirname(output_file)
            if "%" in instance.data["outputPath"]:
                parent_dir = os.path.dirname(output_seq)

                frame = int(re.findall(pattern, f)[0][1:-1])
                dst = output_seq % frame

            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir)

            shutil.copy(f, dst)

            # delete output
            os.remove(f)

            self.log.info("Moved {0} to {1}".format(f, dst))

        # ftrack data
        name = str(instance)
        instance.data["ftrackComponents"][name] = {"path": output_seq}
