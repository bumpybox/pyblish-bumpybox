import os
import json

import pyblish.api


class CollectMovie(pyblish.api.InstancePlugin):
    """ Generate movie job """

    order = pyblish.api.CollectorOrder + 0.1
    families = ["img.*"]

    def process(self, instance):

        # prevent render files to generate movies
        if os.path.splitext(instance.data["family"])[1] in [".ifd"]:
            return

        job = instance.context.data("deadlineJob")
        data = job.GetJobExtraInfoKeyValueWithDefault("PyblishInstanceData",
                                                      "")
        if not data:
            return

        data = json.loads(data)

        for path in instance.data["files"]:

            new_instance = instance.context.create_instance(name=str(instance))

            for key in data:
                instance.data[key] = data[key]

            # prevent resubmitting same job
            del instance.data["deadlineData"]
            instance.data["families"].remove("deadline")

            new_instance.data["family"] = "mov.farm.mov"
            new_instance.data["families"] = ["mov.*", "mov.farm.*", "deadline"]
            new_instance.data["files"] = {}

            frame_padding = instance.data["framePadding"]
            padding_string = ".%{0}d".format(str(frame_padding).zfill(2))
            output_path = path.replace(padding_string, "")
            output_path = os.path.splitext(output_path)[0] + ".mov"
            new_instance.data["framePadding"] = frame_padding

            # setting job data
            job_data = {}
            job_data["Plugin"] = "FFmpeg"
            job_data["Frames"] = "{0}-{1}".format(job.JobFramesList[0],
                                                  job.JobFramesList[-1])
            job_data["Name"] = job.Name
            job_data["UserName"] = job.UserName
            job_data["OutputFilename0"] = output_path
            job_data["ChunkSize"] = job.JobFramesList[-1]

            # setting plugin data
            plugin_data = {}
            plugin_data["InputFile0"] = path
            plugin_data["OutputFile"] = output_path
            plugin_data["ReplacePadding"] = False
            plugin_data["UseSameInputArgs"] = False

            start_frame = str(job.JobFramesList[0])
            inputs_args = "-gamma 2.2 -framerate 25 -start_number "
            inputs_args += start_frame
            plugin_data["InputArgs0"] = inputs_args

            output_args = "-q:v 0 -pix_fmt yuv420p -vf scale=trunc(iw/2)*2:"
            output_args += "trunc(ih/2)*2,colormatrix=bt601:bt709"
            output_args += " -timecode 00:00:00:01"
            plugin_data["OutputArgs"] = output_args

            # setting data
            data = {"job": job_data, "plugin": plugin_data}
            new_instance.data["deadlineData"] = data
