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

    def get_version(self, string, prefix):
        """ Extract version information from filenames.  Code from Foundry"s
        nukescripts.get_version()
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

    def get_version_collections(self, collection, version):
        """Return all collections of previous collection versions."""

        collections = []
        for count in range(1, int(version)):
            version_string = "v" + str(count).zfill(len(version))
            head = collection.head.replace(
                "v" + version, version_string
            )

            version_collection = clique.Collection(
                head=head.replace("\\", "/"),
                padding=collection.padding,
                tail=collection.tail
            )
            version_collection.name = collection.name
            version_collection.label = collection.label
            version_collection.family = collection.family
            version_collection.version = count
            version_collection.nodes = collection.nodes
            collections.append(version_collection)

        return collections

    def single_file_instances(self, instance, version, family_type, context):

        for count in range(1, int(version)):
            version_string = "v" + str(count).zfill(len(version))
            filename = instance.data["output_path"].replace(
                "v" + version, version_string
            )

            if not os.path.exists(filename):
                continue

            new_instance = context.create_instance(
                name=instance.data["name"],
                label="{0} - {1}".format(
                    instance.data["name"], os.path.basename(filename)
                ),
                family="output",
                families=[family_type[0]],
                publish=False,
                output_path=filename,
                version=context.data["version"]
            )

            for node in instance:
                new_instance.add(node)

    def scan_collections_files(self, collections):
        """Return all files in the directories of the collections."""

        scanned_dirs = []
        files = []
        for collection in collections:
            scan_dir = os.path.dirname(collection.head)
            if scan_dir not in scanned_dirs and os.path.exists(scan_dir):
                for f in os.listdir(scan_dir):
                    file_path = os.path.join(scan_dir, f)
                    files.append(file_path.replace("\\", "/"))
                scanned_dirs.append(scan_dir)

        return files

    def populate_collection(self, collection, files):
        """Match and add files to collection.

        Returns populated collection.
        """

        for f in files:
            if collection.match(f):
                collection.add(f)

        return collection

    def process(self, context):

        # Gather all valid collections
        valid_families = ["img", "cache", "scene", "mov", "camera", "geometry"]
        invalid_families = ["read"]
        collections = []
        instances = context + context.data.get("instances", [])
        for instance in instances:

            families = instance.data.get("families", [])
            families += [instance.data["family"]]

            invalid_family = list(set(families) & set(invalid_families))
            if invalid_family:
                continue

            family_type = list(set(families) & set(valid_families))
            if not family_type:
                continue

            instance_collection = instance.data.get("collection", None)

            if instance_collection:

                collection = clique.Collection(
                    head=instance_collection.head,
                    padding=instance_collection.padding,
                    tail=instance_collection.tail
                )

                # Store instance data on collection for later usage
                collection.name = instance.data["name"]
                collection.label = instance.data["label"]
                collection.family = family_type[0]
                collection.version = context.data["version"]
                collection.nodes = instance[:]

                # Get older version collections
                version = self.get_version(
                    os.path.basename(collection.format()), "v"
                )
                if version:
                    collections.extend(
                        self.get_version_collections(
                            collection, version[1]
                        )
                    )

            # Single file outputs
            output_path = instance.data.get("output_path", "")

            if output_path:

                # Get older version collections
                version = self.get_version(
                    os.path.basename(output_path), "v"
                )
                if version:
                    self.single_file_instances(
                        instance, version[1], family_type, context
                    )

        files = self.scan_collections_files(collections)

        # Generate instances from collections
        populated_collections = []
        for collection in collections:

            collection = self.populate_collection(
                collection, files
            )

            if not list(collection):
                continue

            # Ensure collections are unique
            if collection in populated_collections:
                continue
            else:
                populated_collections.append(collection)

            instance = context.create_instance(name=collection.name)

            label = collection.label.split("-")[0] + "- "
            fmt = "{head}{padding}{tail}"
            label += os.path.basename(collection.format(fmt))
            label += collection.format(" [{ranges}]")
            instance.data["label"] = label

            instance.data["families"] = [collection.family]
            instance.data["family"] = "output"
            instance.data["publish"] = False
            instance.data["collection"] = collection
            instance.data["version"] = collection.version

            for node in collection.nodes:
                instance.add(node)
