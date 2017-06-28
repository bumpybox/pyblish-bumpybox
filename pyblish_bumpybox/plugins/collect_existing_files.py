import os
import re

import pyblish.api
import clique


class CollectExistingFiles(pyblish.api.ContextPlugin):
    """Collect all existing files from the collection.

    Offset to iterate over all collected instances.
    """

    order = pyblish.api.CollectorOrder + 0.25
    label = "Existing Files"
    hosts = ["maya", "houdini", "nuke", "nukestudio"]

    scanned_dirs = []
    files = []

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
            self.log.debug(msg)
            return None
        return matches[-1:][0][1], re.search("\d+", matches[-1:][0]).group()

    def scan_versions(self, instance_collection, version):

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

            collection = self.scan_collection(collection)

            if list(collection):
                collections.append(collection)

        return collections

    def scan_collection(self, collection):

        # Scan collection directory
        scan_dir = os.path.dirname(collection.head)
        if scan_dir not in self.scanned_dirs and os.path.exists(scan_dir):
            for f in os.listdir(scan_dir):
                file_path = os.path.join(scan_dir, f)
                self.files.append(file_path.replace("\\", "/"))
            self.scanned_dirs.append(scan_dir)

        # Match files to collection and add
        for f in self.files:
            if collection.match(f):
                collection.add(f)

        return collection

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
        for instance in valid_instances:
            instance_collection = instance.data.get("collection", None)

            if not instance_collection:
                continue

            version = self.version_get(
                os.path.basename(instance_collection.format()), "v"
            )

            collections = []
            if version:
                collections = self.scan_versions(
                    instance_collection, version[1]
                )
            else:
                collection = self.scan_collection(instance_collection)
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

                    new_instance.data["families"] = list(families)
                    new_instance.data["family"] = "output"
                    new_instance.data["publish"] = False
                    new_instance.data["collection"] = collection

                    # If the collection does not have a version,
                    # we'll take the context version.
                    if hasattr(collection, "version"):
                        new_instance.data["version"] = collection.version
                    else:
                        new_instance.data["version"] = context.data["version"]

                    for node in instance:
                        new_instance.add(node)
