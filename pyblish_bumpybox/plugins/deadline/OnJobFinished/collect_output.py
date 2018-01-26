from pyblish_bumpybox import plugin


class CollectOutput(plugin.ContextPlugin):
    """ Collects output """

    order = plugin.CollectorOrder

    def process(self, context):
        import os
        import json

        import clique

        job = context.data["deadlineJob"]

        data = job.GetJobExtraInfoKeyValueWithDefault("PyblishInstanceData",
                                                      "")
        if not data:
            return

        data = json.loads(data)

        # Remove all files that does not exist.
        collection = clique.parse(data["collection"])
        for f in collection:
            if not os.path.exists(f):
                collection.remove(f)

        # Creating instance if collections exists.
        if list(collection):
            instance = context.create_instance(name=data["name"])
            for key in data:
                instance.data[key] = data[key]

            # Prevent resubmitting same job and changing the processing
            # location to local.
            del instance.data["deadlineData"]
            instance.data["families"].remove("deadline")
            instance.data["families"].append("local")

            instance.data["collection"] = collection
