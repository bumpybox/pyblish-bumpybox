import os
import re
import json

import pyblish.api


class CollectRender(pyblish.api.ContextPlugin):
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
        if os.path.splitext(instance_data["family"])[1] not in [".ifd"]:
            return

        instance = context.create_instance(name=instance_data["name"])
        path = instance_data["renderOutputPath"].replace("$F4", "####")
        ext = os.path.splitext(path)[1]
        instance.data["family"] = "img.farm" + ext
        instance.data["families"] = ["img.*", "img.farm.*", "deadline"]
        instance.data["familyParent"] = instance_data["family"]
        instance.data["outputPath"] = instance_data["outputPath"]

        for key in instance_data.keys():
            if key.startswith("ftrack"):
                instance.data[key] = instance_data[key]

        # setting job data
        job_data = {}
        job_data["Plugin"] = "Mantra"
        job_data["Frames"] = job.JobFrames
        job_data["Name"] = job.Name
        job_data["JobDependency0"] = job.JobId
        job_data["OutputFilename0"] = path
        job_data["IsFrameDependent"] = True

        # setting plugin data
        plugin_data = {}
        plugin_data["Version"] = job.GetJobPluginInfoKeyValue("Version")

        # Change out deadline "#" padding for python-style padding
        path = os.path.join(job.OutputDirectories[0], job.OutputFileNames[0])
        match = re.search("#+", path)
        if match:
            padding = match.group(0)
            len_pad = len(padding)
            path = "{0}".format(path.replace(padding, "%%0%dd" % len_pad))

        plugin_data["SceneFile"] = path % job.Frames[0]

        # setting data
        data = {"job": job_data, "plugin": plugin_data}
        instance.data["deadlineData"] = data
