import os

import nuke

import pyblish.api
import clique


class ExtractBakedColorspace(pyblish.api.InstancePlugin):
    """Extracts jpegs with baked in luts"""

    order = pyblish.api.ExtractorOrder
    label = "Baked Colorspace"
    optional = True
    families = ["img"]

    def process(self, instance):
        # Store selection
        selection = [i for i in nuke.allNodes() if i["selected"].getValue()]

        # Deselect all nodes to prevent external connections
        [i["selected"].setValue(False) for i in nuke.allNodes()]

        # Create nodes
        viewer_process_node = nuke.ViewerProcess.node()

        dag_node = None
        if viewer_process_node:
            dag_node = nuke.createNode(viewer_process_node.Class())

            # Copy viewer process values
            excludedKnobs = ["name", "xpos", "ypos"]
            for item in viewer_process_node.knobs().keys():
                if item not in excludedKnobs and item in dag_node.knobs():
                    x1 = viewer_process_node[item]
                    x2 = dag_node[item]
                    x2.fromScript(x1.toScript(False))
        else:
            self.log.warning("No viewer node found.")

        node = instance[0]

        # Read from Write node
        if node.Class() == "Write":
            node["reading"].setValue(True)

        write_node = nuke.createNode("Write")
        path = nuke.filename(node)
        ext = os.path.splitext(path)[1]
        path = path.replace(ext, "_baked_colorspace.jpeg")
        write_node["file"].setValue(path)
        write_node["file_type"].setValue("jpeg")
        write_node["_jpeg_quality"].setValue(1)
        write_node["raw"].setValue(1)

        if dag_node:
            dag_node.setInput(0, node)
            write_node.setInput(0, dag_node)
        else:
            write_node.setInput(0, node)

        first_frame = min(instance.data["collection"].indexes)
        last_frame = max(instance.data["collection"].indexes)

        # Render frames
        nuke.execute(write_node.name(), int(first_frame), int(last_frame))

        nuke.delete(write_node)

        # Disable read from Write node
        if node.Class() == "Write":
            node["reading"].setValue(False)
            node["postage_stamp"].setValue(False)

        # Restore selection
        [i["selected"].setValue(False) for i in nuke.allNodes()]
        [i["selected"].setValue(True) for i in selection]

        if dag_node:
            nuke.delete(dag_node)

        collection = clique.Collection(
            head=instance.data["collection"].head,
            padding=instance.data["collection"].padding,
            tail="_baked_colorspace.jpeg"
        )
        collection.indexes.update(instance.data["collection"].indexes)
        instance.data["colorspace_collection"] = collection
