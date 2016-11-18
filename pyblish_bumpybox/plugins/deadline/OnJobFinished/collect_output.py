import os
import re
import json

import pyblish.api
import clique


class CollectOutput(pyblish.api.ContextPlugin):
    """ Collects output """

    order = pyblish.api.CollectorOrder

    def process(self, context):

        job = context.data["deadlineJob"]

        data = job.GetJobExtraInfoKeyValueWithDefault("PyblishInstanceData",
                                                      "")
        if not data:
            return

        data = json.loads(data)

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
            # Remove all files that does not exist.
            files = []
            for f in collection:
                files.append(f)

            for f in files:
                if not os.path.exists(f):
                    collection.remove(f)

            # Only if some files exists will we add the collection.
            if list(collection):
                collections.append(collection)

        # Creating instance if collections exists.
        if collections:
            instance = context.create_instance(name=data["name"])
            for key in data:
                instance.data[key] = data[key]

            # Prevent resubmitting same job.
            del instance.data["deadlineData"]
            instance.data["families"].remove("deadline")

            instance.data["collections"] = collections
            self.log.debug("Found files: " + str(collections))
