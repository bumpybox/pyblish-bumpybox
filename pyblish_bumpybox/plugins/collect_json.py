import os
import json
import re

import pyblish.api
import clique


class BumpyboxCollectJSON(pyblish.api.ContextPlugin):
    """ Collecting the json files in current directory. """

    label = "JSON"
    order = pyblish.api.CollectorOrder + 0.1
    hosts = ["ftrack"]

    def version_get(self, string, prefix):
        """ Extract version information from filenames.  Code from Foundry"s
        nukescripts.version_get()
        """

        if string is None:
            raise ValueError("Empty version string - no match")

        regex = "[/_.]"+prefix+"\d+"
        matches = re.findall(regex, string, re.IGNORECASE)
        if not len(matches):
            msg = "No \"_"+prefix+"#\" found in \""+string+"\""
            raise ValueError(msg)
        return matches[-1:][0][1], re.search("\d+", matches[-1:][0]).group()

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
        scanned_dirs = []
        files = []
        collections = []
        for data in valid_data:
            if "collection" not in data.keys() or "output" in data["families"]:
                continue

            instance_collection = clique.parse(data["collection"])

            version = self.version_get(
                os.path.basename(instance_collection.format()), "v"
            )[1]

            # Getting collections of all previous versions and current version
            for count in range(1, int(version) + 1):

                # Generate collection
                version_string = "v" + str(count).zfill(len(version))
                head = instance_collection.head.replace(
                    "v" + version, version_string
                )
                collection = clique.Collection(
                    head=head,
                    padding=instance_collection.padding,
                    tail=instance_collection.tail
                )
                collection.version = count

                # Scan collection directory
                scan_dir = os.path.dirname(collection.head)
                if scan_dir not in scanned_dirs and os.path.exists(scan_dir):
                    for f in os.listdir(scan_dir):
                        file_path = os.path.join(scan_dir, f)
                        files.append(file_path.replace("\\", "/"))
                    scanned_dirs.append(scan_dir)

                # Match files to collection and add
                for f in files:
                    if collection.match(f):
                        collection.add(f)

                # Skip if no files were found in the collection
                if not list(collection):
                    continue

                # Skip existing collections
                if collection in collections:
                    continue

                instance = context.create_instance(name=data["name"])
                version = self.version_get(
                    os.path.basename(collection.format()), "v"
                )[1]

                basename = os.path.basename(collection.format())
                instance.data["label"] = "{0} - {1}".format(
                    data["name"], basename
                )

                families = set(valid_families) & set(data["families"])
                instance.data["families"] = list(families) + ["output"]
                instance.data["collection"] = collection
                instance.data["version"] = int(version)

                collections.append(collection)
