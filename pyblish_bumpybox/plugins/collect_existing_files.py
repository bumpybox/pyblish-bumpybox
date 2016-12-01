import os

import pyblish.api
import clique


class BumpyboxCollectExistingFiles(pyblish.api.ContextPlugin):
    """ Collect all existing files from the collection. """

    order = pyblish.api.CollectorOrder + 0.1
    label = "Existing Files"

    def process(self, context):

        # Validate instance based on support families.
        valid_families = ["img", "cache", "render"]
        valid_instances = []
        for instance in context:
            families = instance.data.get("families", [])
            family_type = list(set(families) & set(valid_families))
            if family_type:
                valid_instances.append(instance)

        # Create existing output instance.
        for instance in valid_instances:
            collection = instance.data["collection"]
            existing_collection = clique.Collection(
                head=collection.head, padding=collection.padding,
                tail=collection.tail
            )
            for f in collection:
                if os.path.exists(f):
                    existing_collection.add(f)

            if list(existing_collection):
                name = instance.data["name"]
                new_instance = instance.context.create_instance(name=name)

                label = instance.data["label"].split("-")[0] + "- "
                fmt = "{head}{padding}{tail}"
                label += os.path.basename(existing_collection.format(fmt))
                label += existing_collection.format(" [{ranges}]")
                new_instance.data["label"] = label

                families = set(valid_families) & set(instance.data["families"])
                new_instance.data["families"] = list(families)
                new_instance.data["publish"] = False
                new_instance.data["collection"] = existing_collection

                for node in instance:
                    new_instance.add(node)
