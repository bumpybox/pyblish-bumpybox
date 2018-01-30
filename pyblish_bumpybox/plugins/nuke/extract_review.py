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

    def duplicate_node(self, node, to_file=None):
        """Slightly convoluted but reliable(?) way duplicate a node, using
        the same functionality as the regular copy and paste.
        Could almost be done tidily by doing:
        for knobname in src_node.knobs():
            value = src_node[knobname].toScript()
            new_node[knobname].fromScript(value)
        ..but this lacks some subtly like handling custom knobs
        to_file can be set to a string, and the node will be written to a
        file instead of duplicated in the tree
        """
        import nuke

        # Store selection
        orig_selection = nuke.selectedNodes()

        # Select only the target node
        [n.setSelected(False) for n in nuke.selectedNodes()]
        node.setSelected(True)

        # If writing to a file, do that, restore the selection and return
        if to_file is not None:
            nuke.nodeCopy(to_file)
            [n.setSelected(False) for n in orig_selection]
            return

        # Copy the selected node and clear selection again
        nuke.nodeCopy("%clipboard%")
        node.setSelected(False)

        if to_file is None:
            # If not writing to a file, call paste function, and the new node
            # becomes the selected
            nuke.nodePaste("%clipboard%")
            new_node = nuke.selectedNode()

        # Restore original selection
        [n.setSelected(False) for n in nuke.selectedNodes()]
        [n.setSelected(True) for n in orig_selection]

        return new_node

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

        # Reformat for pixelaspect ratio
        node = previous_node = nuke.createNode("Reformat")

        node["type"].setValue(2)
        nuke.selectedNode()["scale"].setValue(
            [1, 1.0 / instance[0].pixelAspect()]
        )
        node["resize"].setValue(5)

        temporary_nodes.append(node)

        # Baked viewer node
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

        viewer_nodes = nuke.allNodes(filter="Viewer")
        if viewer_nodes:
            viewer_node = nuke.allNodes(filter="Viewer")[0]
            if viewer_node["input_process"].value():
                input_process_node = self.duplicate_node(
                    nuke.toNode(viewer_node["input_process_node"].value())
                )
                input_process_node.setInput(0, previous_node)
                previous_node = input_process_node
                temporary_nodes.append(input_process_node)

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
