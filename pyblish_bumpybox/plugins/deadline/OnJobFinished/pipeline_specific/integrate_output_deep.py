import os
import shutil
import re

import pyblish.api
import pipeline_schema


class IntegrateOutputDeep(pyblish.api.InstancePlugin):
    """ Integrates output """

    families = ["img.*"]
    order = pyblish.api.IntegratorOrder

    def process(self, instance):

        # we won't integrate render files as they will be rendering
        if os.path.splitext(instance.data["family"])[1] in [".ifd"]:
            return

        task_id = instance.context.data["ftrackData"]["Task"]["id"]
        data = pipeline_schema.get_data(task_id)
        data["extension"] = "exr"
        data["output_type"] = instance.data["ftrackAssetType"]
        data["name"] = instance.data["name"] + "_deep"
        data["version"] = instance.context.data["version"]
        output_seq = pipeline_schema.get_path("output_sequence", data=data)

        output_path = instance.data["outputPath"]

        pattern = os.path.basename(output_path)
        frame_padding = instance.data["framePadding"]
        padding_string = ".%{0}d.".format(str(frame_padding).zfill(2))
        pattern = pattern.replace(padding_string, r"_deep\.([0-9]{4,})\.")
        pattern = pattern.replace(".ifd", ".exr")
        self.log.debug("Pattern generated: " + pattern)

        current_dir = os.path.dirname(output_path)
        self.log.info("Searching in: " + current_dir)
        for f in os.listdir(current_dir):
            if re.match(pattern, f):
                f = os.path.join(current_dir, f)

                frame = int(re.findall(pattern, f)[0])
                dst = output_seq % frame

                if not os.path.exists(os.path.dirname(output_seq)):
                    os.makedirs(os.path.dirname(output_seq))

                shutil.copy(f, dst)

                # delete output
                os.remove(f)

                self.log.info("Moved {0} to {1}".format(f, dst))

        # ftrack data
        name = instance.data["name"] + "_deep"
        instance.data["ftrackComponents"][name] = {"path": output_seq}
