import os

import pyblish.api


class ExtractViewerLut(pyblish.api.InstancePlugin):
    """Extract the Nuke viewer LUT"""

    order = pyblish.api.ExtractorOrder
    label = "Viewer LUT"
    families = ["img", "mov"]
    hosts = ["nuke"]
    optional = True

    def process(self, instance):
        import nuke

        # Deselect all nodes to prevent external connections
        [i["selected"].setValue(False) for i in nuke.allNodes()]

        # Create nodes
        viewer_process_node = nuke.ViewerProcess.node()
        cms_node = nuke.createNode("CMSTestPattern")
        dag_node = nuke.createNode(viewer_process_node.Class())
        generate_lut_node = nuke.createNode("GenerateLUT")

        # Copy viewer process values
        excludedKnobs = ["name", "xpos", "ypos"]
        for item in viewer_process_node.knobs().keys():
            if item not in excludedKnobs and item in dag_node.knobs():
                x1 = viewer_process_node[item]
                x2 = dag_node[item]
                x2.fromScript(x1.toScript(False))

        # Setup generate lut node
        path = None
        if "collection" in instance.data.keys():
            collection = instance.data["collection"]
            path = collection.format("{head}.cube")
        if "output_path" in instance.data.keys():
            path = os.path.splitext(instance.data["output_path"])[0]
            path += ".cube"

        generate_lut_node["file"].setValue(path.replace("\\", "/"))
        generate_lut_node["file_type"].setValue(6)

        # Extract LUT file
        nuke.execute(generate_lut_node, 0, 0)

        # Clean up nodes
        nuke.delete(cms_node)
        nuke.delete(dag_node)
        nuke.delete(generate_lut_node)
