import json

import pyblish.api


class AppendDeadlineData(pyblish.api.InstancePlugin):
    """ Append Deadline data """

    order = pyblish.api.ExtractorOrder
    families = ["img.farm.*"]

    def process(self, instance):

        if ("familyParent" in instance.data and
           instance.data["familyParent"].endswith("ifd")):

            job = instance.context.data("deadlineJob")
            value = job.GetJobExtraInfoKeyValue("PyblishInstanceData")
            instance_data = json.loads(value)

            # setting job data
            group = instance_data["deadlineData"]["job"]["Group"]
            group = group.replace("houdini", "mantra")
            instance.data["deadlineData"]["job"]["Group"] = group
