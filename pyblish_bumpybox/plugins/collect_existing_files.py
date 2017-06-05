import os
import re

import pyblish.api
import clique


class CollectExistingFiles(pyblish.api.ContextPlugin):
    """ Collect all existing files from the collection. """

    order = pyblish.api.CollectorOrder + 0.1
    label = "Existing Files"
    hosts = ["maya", "houdini", "nuke"]

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

        # Validate instance based on support families.
        valid_families = ["img", "cache", "scene", "mov"]
        valid_instances = []
        for instance in context:
            families = instance.data.get("families", [])
            family_type = list(set(families) & set(valid_families))
            if family_type:
                valid_instances.append(instance)

        # Create existing output instance.
        scanned_dirs = []
        files = []
        for instance in valid_instances:
            instance_collection = instance.data.get("collection", None)

            if not instance_collection:
                continue

            version = self.version_get(
                os.path.basename(instance_collection.format()), "v"
            )[1]

            # Getting collections of all previous versions and current version
            collections = []
            for count in range(1, int(version) + 1):

                # Generate collection
                version_string = "v" + str(count).zfill(len(version))
                head = instance_collection.head.replace(
                    "v" + version, version_string
                )
                collection = clique.Collection(
                    head=head.replace("\\", "/"),
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

                if list(collection):
                    collections.append(collection)

            if collections:
                families = set(valid_families) & set(instance.data["families"])
                for collection in collections:
                    name = instance.data["name"]
                    new_instance = instance.context.create_instance(name=name)

                    label = instance.data["label"].split("-")[0] + "- "
                    fmt = "{head}{padding}{tail}"
                    label += os.path.basename(collection.format(fmt))
                    label += collection.format(" [{ranges}]")
                    new_instance.data["label"] = label

                    new_instance.data["families"] = list(families) + ["output"]
                    new_instance.data["family"] = list(families)[0]
                    new_instance.data["publish"] = False
                    new_instance.data["collection"] = collection
                    new_instance.data["version"] = collection.version

                    for node in instance:
                        new_instance.add(node)
