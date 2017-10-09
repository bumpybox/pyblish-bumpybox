import os

import nuke

import pyblish.api


class ExtractViewerLut(pyblish.api.InstancePlugin):
    """Extract the Nuke viewer LUT"""

    order = pyblish.api.ExtractorOrder
    label = "Viewer LUT"
    families = ["img", "mov"]
    hosts = ["nuke"]
    optional = True

    def get_colorspace_index(self, node):
        """Get colorspace node index corresponding to the node's colorspace."""

        colorspace_values = [
            "1.80\tgamma 1.80", "2.20\tgamma 2.20", "2.40\tgamma 2.40",
            "rec709\trec709 (~1.95)", "sRGB\tsRGB (~2.20)", "Cineon",
            "RGB\tLinear", "HSV", "HSL", "YPbPr", "YCbCr", "CIE-XYZ",
            "CIE-Yxy", "CIE-Lab\tL*a*b*", "CIE-LCH", "Panalog", "REDLog",
            "ViperLog", "AlexaV3LogC", "PLogLin", "SLog", "SLog1", "SLog2",
            "SLog3", "CLog", "Protune"
        ]

        node_values = [
            "default", "linear", "sRGB", "rec709", "Cineon", "Gamma1.8",
            "Gamma2.2", "Gamma2.4", "Panalog", "REDLog", "ViperLog",
            "AlexaV3LogC", "PLogLin", "SLog", "SLog1", "SLog2", "SLog3",
            "CLog", "Protune", "REDSpace"
        ]

        colorspace_mapping = {
            "linear": "RGB\tLinear",
            "sRGB": "sRGB\tsRGB (~2.20)",
            "rec709": "rec709\trec709 (~1.95)",
            "Cineon": "Cineon",
            "Gamma1.8": "1.80\tgamma 1.80",
            "Gamma2.2": "2.20\tgamma 2.20",
            "Gamma2.4": "2.40\tgamma 2.40",
            "Panalog": "Panalog",
            "REDLog": "REDLog",
            "ViperLog": "ViperLog",
            "AlexaV3LogC": "AlexaV3LogC",
            "PLogLin": "PLogLin",
            "SLog": "SLog",
            "SLog1": "SLog1",
            "SLog2": "SLog2",
            "SLog3": "SLog3",
            "CLog": "CLog",
            "Protune": "Protune",
        }

        extension_mapping = {
            "mov": "2.20\tgamma 2.20",
            "dpx": "Cineon",
            "exr": "RGB\tLinear"
        }

        value = node["colorspace"].getValue()
        colorspace_index = 0
        if value == 0:
            extension = ""

            if node.Class() == "Read":
                extension = node.metadata()["input/filereader"]
            if node.Class() == "Write":
                extension = node["file_type"].value()

            colorspace_index = colorspace_values.index(
                extension_mapping[extension]
            )
        else:
            colorspace_index = colorspace_values.index(
                colorspace_mapping[node_values[int(value)]]
            )

        return colorspace_index

    def process(self, instance):

        # Deselect all nodes to prevent external connections
        [i["selected"].setValue(False) for i in nuke.allNodes()]

        # Create nodes
        viewer_process_node = nuke.ViewerProcess.node()
        cms_node = nuke.createNode("CMSTestPattern")
        colorspace_node = nuke.createNode("Colorspace")
        dag_node = nuke.createNode(viewer_process_node.Class())
        generate_lut_node = nuke.createNode("GenerateLUT")

        # Copy viewer process values
        excludedKnobs = ["name", "xpos", "ypos"]
        for item in viewer_process_node.knobs().keys():
            if item not in excludedKnobs and item in dag_node.knobs():
                x1 = viewer_process_node[item]
                x2 = dag_node[item]
                x2.fromScript(x1.toScript(False))

        # Setup colorspace node
        colorspace_node["colorspace_in"].setValue(
            self.get_colorspace_index(instance[0])
        )

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
        nuke.delete(colorspace_node)
        nuke.delete(dag_node)
        nuke.delete(generate_lut_node)
