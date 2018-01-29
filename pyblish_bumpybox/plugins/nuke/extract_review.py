from pyblish import api
from pyblish_bumpybox import inventory


class ExtractReview(api.InstancePlugin):
    """Extracts image sequence with baked in luts

    Offset from:
        pyblish_bumpybox.plugins.nuke.extract_nuke_write.ExtractNukeWrite
    """

    label = "Nuke Review"
    optional = True
    order = inventory.get_order(__file__, "ExtractReview")
    targets = ["process.local"]
    families = ["img"]

    def process(self, instance):
        import os
        import tempfile
        import shutil

        import clique

        import nuke

        # Store selection
        selection = [i for i in nuke.allNodes() if i["selected"].getValue()]

        # Deselect all nodes to prevent external connections
        [i["selected"].setValue(False) for i in nuke.allNodes()]

        temporary_nodes = []

        # Create nodes
        first_frame = min(instance.data["collection"].indexes)
        last_frame = max(instance.data["collection"].indexes)

        temp_dir = tempfile.mkdtemp()
        for f in instance.data["collection"]:
            shutil.copy(f, os.path.join(temp_dir, os.path.basename(f)))

        node = previous_node = nuke.createNode("Read")
        node["file"].setValue(
            os.path.join(
                temp_dir,
                os.path.basename(
                    instance.data["collection"].format(
                        "{head}{padding}{tail}"
                    )
                )
            ).replace("\\", "/")
        )
        node["first"].setValue(first_frame)
        node["origfirst"].setValue(first_frame)
        node["last"].setValue(last_frame)
        node["origlast"].setValue(last_frame)

        index = instance[0]["colorspace"].getValue()
        node["colorspace"].setValue(node["colorspace"].enumName(int(index)))

        temporary_nodes.append(node)

        viewer_process_node = nuke.ViewerProcess.node()

        dag_node = None
        if viewer_process_node:
            dag_node = nuke.createNode(viewer_process_node.Class())
            dag_node.setInput(0, previous_node)
            previous_node = dag_node
            temporary_nodes.append(dag_node)
            # Copy viewer process values
            excludedKnobs = ["name", "xpos", "ypos"]
            for item in viewer_process_node.knobs().keys():
                if item not in excludedKnobs and item in dag_node.knobs():
                    x1 = viewer_process_node[item]
                    x2 = dag_node[item]
                    x2.fromScript(x1.toScript(False))
        else:
            self.log.warning("No viewer node found.")

        write_node = nuke.createNode("Write")
        head = instance.data["collection"].format(
            "{head}_review."
        )
        if instance.data["collection"].format("{head}").endswith("."):
            head = instance.data["collection"].format("{head}")[:-1]
            head += "_review."
        review_collection = clique.Collection(
            head=head,
            padding=4,
            tail=".jpeg"
        )
        review_collection.indexes.update(instance.data["collection"].indexes)
        write_node["file"].setValue(
            review_collection.format(
                "{head}{padding}{tail}"
            ).replace("\\", "/")
        )
        write_node["file_type"].setValue("jpeg")
        write_node["raw"].setValue(1)
        write_node["_jpeg_quality"].setValue(1)
        write_node.setInput(0, previous_node)
        temporary_nodes.append(write_node)
        instance.data["review_collection"] = review_collection

        # Render frames
        nuke.execute(write_node.name(), int(first_frame), int(last_frame))

        # Clean up
        for node in temporary_nodes:
            nuke.delete(node)

        shutil.rmtree(temp_dir)

        # Restore selection
        [i["selected"].setValue(False) for i in nuke.allNodes()]
        [i["selected"].setValue(True) for i in selection]
