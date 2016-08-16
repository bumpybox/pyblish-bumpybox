import os
import shutil
import re

import pyblish.api
import pipeline_schema


class IntegrateOutput(pyblish.api.InstancePlugin):
    """ Integrates output """

    families = ["cache.*", "img.*", "mov.*"]
    order = pyblish.api.IntegratorOrder

    def process(self, instance):

        # required data members for successfull integration
        if ("ftrackAssetType" not in instance.data and
           "files" not in instance.data):
            return

        # do not integrate render files
        if os.path.splitext(instance.data["family"])[1] in [".ifd"]:
            return

        # get output path, extension is "temp" as we"ll get the extension from
        # the output files
        task_id = instance.context.data["ftrackData"]["Task"]["id"]
        data = pipeline_schema.get_data(task_id)
        ext = os.path.splitext(instance.data["family"])[1].replace("_", ".")
        data["extension"] = ext[1:]
        data["output_type"] = instance.data["ftrackAssetType"]
        data["name"] = str(instance)
        data["version"] = instance.context.data["version"]
        output_file = pipeline_schema.get_path("output_file", data=data)

        frame_padding = instance.data["framePadding"]
        padding_string = ".%{0}d.".format(str(frame_padding).zfill(2))
        output_seq = pipeline_schema.get_path("output_sequence", data=data)
        output_seq = output_seq.replace(".%04d.", padding_string)

        components = {}
        paths = {}
        for path in instance.data["files"].keys():

            # moving output
            pattern = r"\.[0-9]+\."
            files = []
            output = output_file
            for f in instance.data["files"][path]:

                dst = output_file

                # get frame number
                if "%" in path:
                    frame = re.findall(pattern, os.path.basename(f))[-1]
                    frame = int(frame[1:-1])
                    dst = output_seq % frame
                    output = output_seq

                files.append(dst)

                # create root
                if not os.path.exists(os.path.dirname(dst)):
                    os.makedirs(os.path.dirname(dst))

                # moving file
                if f != dst:
                    shutil.copy(f, dst)

                    self.log.info("Copied {0} to {1}".format(f, dst))

            paths[output.replace(".temp", ext)] = files

            # ftrack data
            component_name = str(instance)
            if len(instance.data["files"]) > 1:
                index = instance.data["files"].keys().index(path)
                component_name = "{0}_{1}".format(component_name, str(index))

            components[component_name] = {"path": output.replace(".temp", ext)}

        # adding component data
        instance.data["ftrackComponents"] = components
