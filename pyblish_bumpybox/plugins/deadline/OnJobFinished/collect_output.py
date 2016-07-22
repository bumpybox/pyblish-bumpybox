import os
import re
import json

import pyblish.api


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
            directory = os.path.dirname(path)
            ext = os.path.splitext(path)[1]
            start_base = os.path.basename(path).split("%")[0]

            collection = []
            for f in os.listdir(directory):
                if f.startswith(start_base) and f.endswith(ext):
                    collection.append(os.path.join(directory, f))

            files[path] = collection

        # creating instance
        instance = context.create_instance(name=data["name"])
        for key in data:
            instance.data[key] = data[key]

        instance.data["files"] = files
        self.log.debug("Found files: " + str(files))
