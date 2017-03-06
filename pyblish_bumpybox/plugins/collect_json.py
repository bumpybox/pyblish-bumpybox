import os
import json

import pyblish.api
import clique


class BumpyboxCollectJSON(pyblish.api.ContextPlugin):
    """ Collecting the json files in current directory. """

    label = "JSON"
    order = pyblish.api.CollectorOrder + 0.1
    hosts = ["ftrack"]

    def process(self, context):

        current_file = context.data("currentFile")

        # Skip if current file is not a directory
        if not os.path.isdir(current_file):
            return

        # Traverse directory and collect collections from json files.
        instances = []
        for root, dirs, files in os.walk(current_file):
            for f in files:
                if f.endswith(".json"):
                    with open(os.path.join(root, f)) as json_data:
                        for data in json.load(json_data):
                            instances.append(data)

        # Validate instance based on supported families.
        valid_families = ["img", "cache", "scene", "mov"]
        valid_data = []
        for data in instances:
            families = data.get("families", [])
            family_type = list(set(families) & set(valid_families))
            if family_type:
                valid_data.append(data)

        # Create existing output instance.
        for data in valid_data:
            if "collection" not in data.keys() or "output" in data["families"]:
                continue

            files = clique.parse(data["collection"])
            try:
                files = clique.parse(
                    data["collection"],
                    pattern="{head}{padding}{tail} [{range}]"
                )
            except:
                pass

            collection = clique.Collection(
                head=files.head, padding=files.padding, tail=files.tail
            )
            for f in files:
                if os.path.exists(f):
                    collection.add(f)

            if list(collection):
                instance = context.create_instance(name=data["name"])

                basename = os.path.basename(collection.format())
                instance.data["label"] = "{0} - {1}".format(
                    data["name"], basename
                )

                families = set(valid_families) & set(data["families"])
                instance.data["families"] = list(families) + ["output"]
                instance.data["collection"] = collection
