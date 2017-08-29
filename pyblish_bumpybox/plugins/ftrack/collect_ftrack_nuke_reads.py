import os

import nuke
import pyblish.api
import clique


class CollectFtrackNukeReads(pyblish.api.ContextPlugin):
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

            # Create instance
            instance = context.create_instance(node.name())
            instance.data["families"] = [output_type, "local", "output"]
            instance.data["family"] = "read"
            instance.add(node)

            path = nuke.filename(node)
            instance.data["label"] = "{0} - {1}".format(
                node.name(), os.path.basename(path)
            )

            # Adding/Checking publish attribute
            instance.data["publish"] = False
            if "publish" not in node.knobs():
                knob = nuke.Boolean_Knob("publish", "Publish")
                knob.setValue(False)
                node.addKnob(knob)
            else:
                instance.data["publish"] = node["publish"].getValue()

            # Collecting file paths
            if output_type == "img":
                # This could be improved because it does not account for "#"
                # being in a sequence.
                if "#" in path:
                    padding = path.count("#")
                    path = path.replace(
                        "#" * padding, "%{0:0>2}d".format(padding)
                    )

                first_frame = int(node["first"].getValue())
                last_frame = int(node["last"].getValue())
                path += " [{0}-{1}]".format(first_frame, last_frame)
                instance.data["collection"] = clique.parse(path)
            else:
                instance.data["output_path"] = path
