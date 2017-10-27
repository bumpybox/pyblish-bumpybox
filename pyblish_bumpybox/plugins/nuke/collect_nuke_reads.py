import os

import nuke
import pyblish.api
import clique


class CollectNukeReads(pyblish.api.ContextPlugin):
    """Collect all read nodes."""

    order = pyblish.api.CollectorOrder
    label = "Reads"
    hosts = ["nuke"]

    def process(self, context):

        # creating instances per write node
        for node in nuke.allNodes():
            if node.Class() != "Read":
                continue

            # Determine output type
            output_type = "img"
            movie_formats = ["ari", "avi", "gif", "mov", "r3d"]
            if node.metadata()["input/filereader"] in movie_formats:
                output_type = "mov"
            scene_formats = ["psd"]
            if node.metadata()["input/filereader"] in scene_formats:
                output_type = "scene"

            # Create instance
            instance = context.create_instance(node.name())
            instance.data["families"] = [output_type, "local", "output"]
            instance.data["family"] = "read"
            instance.add(node)

            path = nuke.filename(node)

            # Adding/Checking publish attribute
            if "publish" not in node.knobs():
                knob = nuke.Boolean_Knob("publish", "Publish")
                knob.setValue(False)
                node.addKnob(knob)

            # Compare against selection
            selection = instance.context.data.get("selection", [])
            publish = bool(node["publish"].getValue())
            if selection:
                if list(set(instance) & set(selection)):
                    publish = True
                else:
                    publish = False

            instance.data["publish"] = publish

            # Collecting file paths
            label = "{0} - {1}".format(node.name(), os.path.basename(path))
            if output_type == "img":
                # This could be improved because it does not account for "#"
                # being in a sequence.
                if "#" in path:
                    padding = path.count("#")
                    path = path.replace(
                        "#" * padding, "%{0:0>2}d".format(padding)
                    )

                try:
                    collection = clique.parse(path + " []")
                except ValueError as e:
                    context.remove(instance)
                    self.log.warning(
                        "Collection error on \"{0}\": "
                        "{1}".format(node.name(), e)
                    )
                    continue

                for f in os.listdir(os.path.dirname(path)):
                    file_path = os.path.join(os.path.dirname(path), f)
                    file_path = file_path.replace("\\", "/")
                    if collection.match(file_path):
                        collection.add(file_path)

                instance.data["collection"] = collection
                label = "{0} - {1}".format(
                    node.name(), os.path.basename(collection.format())
                )
            else:
                instance.data["output_path"] = path

            instance.data["label"] = label

            def instanceToggled(instance, value):
                instance[0]["publish"].setValue(value)

            instance.data["instanceToggled"] = instanceToggled
