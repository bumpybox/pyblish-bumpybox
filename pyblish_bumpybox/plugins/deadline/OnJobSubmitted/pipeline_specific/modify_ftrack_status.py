import json

import pyblish.api


class ModifyFtrackStatus(pyblish.api.InstancePlugin):
    """ Modifies ftrack status to False """

    order = pyblish.api.ExtractorOrder
    families = ["img.farm.*"]

    def process(self, instance):

        if ("familyParent" in instance.data and
           instance.data["familyParent"].startswith("render")):

            job = instance.context.data("deadlineJob")
            value = job.GetJobExtraInfoKeyValue("PyblishInstanceData")
            instance_data = json.loads(value)

            instance_data["ftrackStatusUpdate"] = False
            self.log.info(instance_data)

            job.SetJobExtraInfoKeyValue("PyblishInstanceData",
                                        json.dumps(instance_data))
            self.log.info("Setting \"ftrackStatusUpdate\" to \"False\"")
