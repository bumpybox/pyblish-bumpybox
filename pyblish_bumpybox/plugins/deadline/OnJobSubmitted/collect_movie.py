from pyblish_bumpybox import plugin


class CollectMovie(plugin.ContextPlugin):
    """ Generate movie instance and job. """

    order = plugin.CollectorOrder

    def process(self, context):
        import json

        import clique

        job = context.data("deadlineJob")
        data = job.GetJobExtraInfoKeyValueWithDefault(
            "PyblishInstanceData", ""
        )
        if not data:
            return

        data = json.loads(data)

        if "img" not in data["families"]:
            self.log.info("Could not find \"img\" in families.")
            return

        # Prevent resubmitting same job
        del data["deadlineData"]
        data["families"].remove("deadline")

        name = data["name"]
        instance = context.create_instance(name=name)
        instance.data["families"] = ["mov", "local", "deadline"]
        img_collection = clique.parse(data["collection"])
        collection = clique.parse(
            img_collection.format(
                "{head}{padding}.mov [" + str(job.JobFramesList[0]) + "]"
            )
        )
        instance.data["collection"] = collection.format()

        for key in data:
            data[key] = data[key]

        # Create FFmpeg dependent job
        job_data = {}
        job_data["Plugin"] = "FFmpeg"
        job_data["Frames"] = "{0}-{1}".format(job.JobFramesList[0],
                                              job.JobFramesList[-1])
        job_data["Name"] = job.Name
        job_data["UserName"] = job.UserName
        job_data["ChunkSize"] = job.JobFramesList[-1] + 1
        job_data["JobDependency0"] = job.JobId

        job_data["OutputFilename0"] = list(collection)[0]

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
        plugin_data["InputFile0"] = img_collection.format(
            "{head}{padding}{tail}"
        )
        plugin_data["ReplacePadding"] = False
        plugin_data["ReplacePadding0"] = False
        plugin_data["UseSameInputArgs"] = False

        plugin_data["OutputFile"] = list(collection)[0]

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
