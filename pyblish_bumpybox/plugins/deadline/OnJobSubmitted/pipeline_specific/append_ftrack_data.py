import json

import pyblish.api


class AppendFtrackData(pyblish.api.InstancePlugin):
    """ Append Deadline data """

    order = pyblish.api.ExtractorOrder
    families = ["img.farm.*"]

    def process(self, instance):

        job = instance.context.data("deadlineJob")
        value = job.GetJobExtraInfoKeyValue("PyblishInstanceData")
        instance_data = json.loads(value)

        instance.data["ftrackComponents"] = {}
        instance.data["ftrackAssetType"] = "img"
        instance.data["ftrackAssetName"] = instance_data["ftrackAssetName"]
