import json
import math

import pyblish.api
import clique


class BumpyboxDeadlineOnJobSubmittedCollectRender(pyblish.api.ContextPlugin):
    """ Integrates render """

    order = pyblish.api.CollectorOrder

    def process(self, context):

        job = context.data("deadlineJob")

        # create instance
        value = job.GetJobExtraInfoKeyValueWithDefault("PyblishInstanceData",
                                                       "")
        if not value:
            return
        instance_data = json.loads(value)

        # return early if it isn't a render file
        render_families = ["ifd"]
        if not list(set(instance_data["families"]) & set(render_families)):
            return

        instance = context.create_instance(name=instance_data["name"])

        for key in instance_data.keys():
            instance.data[key] = instance_data[key]

        instance.data["families"] = ["img", "remote", "deadline"]

        # setting job data
        job_data = {}
        job_data["Plugin"] = "Mantra"
        job_data["Frames"] = job.JobFrames
        job_data["Name"] = job.Name
        job_data["JobDependency0"] = job.JobId
        job_data["IsFrameDependent"] = True

        frame_count = 0
        for f in job.JobFramesList:
            frame_count += 1
        if frame_count > 5000:
            job_data["ChunkSize"] = int(math.ceil(frame_count / 5000.0))

        collection = clique.parse(instance_data["render"])
        fmt = "{head}" + "#" * collection.padding + "{tail}"
        job_data["OutputFilename0"] = collection.format(fmt)

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
        plugin_data["Version"] = job.GetJobPluginInfoKeyValue("Version")

        collection = clique.parse(instance_data["collection"])
        plugin_data["SceneFile"] = list(collection)[0]

        # setting data
        data = {"job": job_data, "plugin": plugin_data}
        instance.data["deadlineData"] = data
