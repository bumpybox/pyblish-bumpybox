import os
import json
import re

import pyblish.api


class CollectOutput(pyblish.api.ContextPlugin):
    """ Collects output """

    order = pyblish.api.CollectorOrder

    def process(self, context):

        job = context.data["deadlineJob"]

        # returning early for old publishes
        if "FT_ProjectId" in job.GetJobExtraInfoKeys():
            return

        task = context.data["deadlineTask"]
        data = job.GetJobExtraInfoKeyValueWithDefault("PyblishInstanceData",
                                                      "")
        if not data:
            return

        data = json.loads(data)

        # collecting all output files
        files = {}
        for i in range(len(job.OutputDirectories)):
            path = os.path.join(job.OutputDirectories[i],
                                job.OutputFileNames[i])

            # Change out deadline "#" padding for python-style padding
            match = re.search("#+", path)
            if match:
                padding = match.group(0)
                len_pad = len(padding)
                path = "{0}".format(path.replace(padding, "%%0%dd" % len_pad))

            # collecting all matching output files
            collection = []
            for f in task.TaskFrameList:
                if os.path.exists(path % f):
                    collection.append(path % f)

            files[path] = collection

        # creating instance
        instance = context.create_instance(name=data["name"])
        for key in data:
            instance.data[key] = data[key]

        # prevent resubmitting same job
        del instance.data["deadlineData"]
        instance.data["families"].remove("deadline")

        instance.data["files"] = files
        self.log.debug("Found files: " + str(files))
