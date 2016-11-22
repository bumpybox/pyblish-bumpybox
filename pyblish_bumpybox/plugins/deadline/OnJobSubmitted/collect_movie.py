import os
import json
import re

import pyblish.api
import clique


class CollectMovie(pyblish.api.ContextPlugin):
    """ Generate movie instance and job. """

    order = pyblish.api.CollectorOrder

    def process(self, context):

        job = context.data("deadlineJob")
        data = job.GetJobExtraInfoKeyValueWithDefault("PyblishInstanceData",
                                                      "")
        if not data:
            return

        data = json.loads(data)

        if "img" not in data["families"]:
            self.log.info("Could not find \"img\" in families.")
            return

        # prevent resubmitting same job
        del data["deadlineData"]
        data["families"].remove("deadline")

        # collecting all output files
        collections = []
        for i in range(len(job.OutputDirectories)):
            path = os.path.join(job.OutputDirectories[i],
                                job.OutputFileNames[i])

            # Find padding len by assuming deadline padding of "#".
            match = re.search("#+", path)
            padding = 0
            if match:
                padding = len(match.group(0))

            # Construct clique collection by parsing string data.
            padding_string = "%{0}d".format(str(padding).zfill(2))
            [head, tail] = path.split("#" * padding)
            collection = clique.parse("{0}{1}{2} [{3}]".format(head,
                                                               padding_string,
                                                               tail,
                                                               job.JobFrames))

            # create collection
            files = []
            for f in collection:
                files.append(f)

            # Only if some files exists will we add the collection.
            if list(collection):
                collections.append(collection)

        for collection in collections:

            name = data["name"]
            instance = context.create_instance(name=name)
            instance.data["families"] = ["mov", "farm", "deadline"]

            for key in data:
                data[key] = data[key]

            # setting job data
            job_data = {}
            job_data["Plugin"] = "FFmpeg"
            job_data["Frames"] = "{0}-{1}".format(job.JobFramesList[0],
                                                  job.JobFramesList[-1])
            job_data["Name"] = job.Name
            job_data["UserName"] = job.UserName
            job_data["ChunkSize"] = job.JobFramesList[-1] + 1
            job_data["JobDependency0"] = job.JobId

            path = collection.format("{head}" + "#" * collection.padding)
            job_data["OutputFilename0"] = path + ".mov"

            # Copy environment keys.
            index = 0
            if job.GetJobEnvironmentKeys():
                for key in job.GetJobEnvironmentKeys():
                    value = job.GetJobEnvironmentKeyValue(key)
                    data = "{0}={1}".format(key, value)
                    job_data["EnvironmentKeyValue" + str(index)] = data
                    index += 1

            # setting plugin data
            plugin_data = {}
            input_file = collection.format("{head}{padding}{tail}")
            plugin_data["InputFile0"] = input_file
            plugin_data["ReplacePadding"] = False
            plugin_data["UseSameInputArgs"] = False

            path = collection.format("{head}{padding}.mov") % 1
            plugin_data["OutputFile"] = path

            start_frame = str(job.JobFramesList[0])
            inputs_args = "-gamma 2.2 -framerate 25 -start_number "
            inputs_args += start_frame
            plugin_data["InputArgs0"] = inputs_args

            if "audio" in instance.context.data:
                plugin_data["InputFile1"] = instance.context.data["audio"]

            output_args = "-q:v 0 -pix_fmt yuv420p -vf scale=trunc(iw/2)*2:"
            output_args += "trunc(ih/2)*2,colormatrix=bt601:bt709"
            output_args += " -timecode 00:00:00:01"
            plugin_data["OutputArgs"] = output_args

            # setting data
            data = {"job": job_data, "plugin": plugin_data}
            instance.data["deadlineData"] = data

            self.log.info(instance)
