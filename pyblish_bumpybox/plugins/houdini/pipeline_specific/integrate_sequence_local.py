import os
import shutil
import re

import pyblish.api
import pipeline_schema


class IntegrateSequenceLocal(pyblish.api.InstancePlugin):
    """ Integrates mantra local output """

    families = ["img.local.*", "render.local.*", "cache.local.geometry"]
    label = "Sequence Local"
    order = pyblish.api.IntegratorOrder
    optional = True

    def process(self, instance):

        data = pipeline_schema.get_data()

        ext = os.path.splitext(instance.data["outputPath"])[1][1:]
        if instance.data["outputPath"].endswith("bgeo.sc"):
            ext = "bgeo.sc"

        data["extension"] = ext
        data["output_type"] = "img"
        if instance.data["family"] == "cache.local.geometry":
            data["output_type"] = "cache"
        data["name"] = str(instance)
        output_seq = pipeline_schema.get_path("output_sequence", data=data)

        # copy output
        if not os.path.exists(os.path.dirname(output_seq)):
            os.makedirs(os.path.dirname(output_seq))

        pattern = r"\.[0-9]{4}\."
        for f in instance.data["outputFiles"]:
            frame = int(re.findall(pattern, f)[0][1:-1])
            dst = output_seq % frame
            shutil.copy(f, dst)

            # delete output
            os.remove(f)

            self.log.info("Moved {0} to {1}".format(f, dst))

        # ftrack data
        name = str(instance)
        instance.data["ftrackComponents"][name] = {"path": output_seq}
