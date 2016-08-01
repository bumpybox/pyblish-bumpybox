import json

import pyblish.api


class AppendFtrackData(pyblish.api.InstancePlugin):
    """ Append Ftrack data """

    order = pyblish.api.CollectorOrder + 0.2
    families = ["mov.*"]

    def process(self, instance):

        job = instance.context.data("deadlineJob")
        value = job.GetJobExtraInfoKeyValue("PyblishInstanceData")
        instance_data = json.loads(value)

        instance.data["ftrackComponents"] = {}
        instance.data["ftrackAssetType"] = "mov"
        instance.data["ftrackAssetName"] = instance_data["ftrackAssetName"]
        instance.data["ftrackStatusUpdate"] = True
