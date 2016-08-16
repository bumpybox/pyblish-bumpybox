import os
import shutil
import re

import pyblish.api
import pipeline_schema


class IntegrateLocalDeep(pyblish.api.InstancePlugin):
    """ Integrates local output """

    families = ["img.local.*"]
    label = "Local Deep"
    order = pyblish.api.IntegratorOrder
    optional = True

    def process(self, instance):

        data = pipeline_schema.get_data()
        ext = os.path.splitext(instance.data["family"])[1].replace("_", ".")
        data["extension"] = ext[1:]
        data["output_type"] = "img"
        data["name"] = str(instance) + "_deep"

        output_seq = pipeline_schema.get_path("output_sequence", data=data)

        # copy output
        if not os.path.exists(os.path.dirname(output_seq)):
            os.makedirs(os.path.dirname(output_seq))

        output_path = instance.data["outputPath"]

        pattern = os.path.basename(output_path)
        frame_padding = instance.data["framePadding"]
        padding_string = ".%{0}d.".format(str(frame_padding).zfill(2))
        pattern = pattern.replace(padding_string, r"_deep\.([0-9]{4,})\.")
        self.log.debug("Pattern generated: " + pattern)

        current_dir = os.path.dirname(output_path)
        for f in os.listdir(current_dir):
            if re.match(pattern, f):
                f = os.path.join(current_dir, f)

                frame = int(re.findall(pattern, f)[0])
                dst = output_seq % frame

                shutil.copy(f, dst)

                # delete output
                os.remove(f)

                self.log.info("Moved {0} to {1}".format(f, dst))

        # ftrack data
        name = str(instance) + "_deep"
        instance.data["ftrackComponents"][name] = {"path": output_seq}
