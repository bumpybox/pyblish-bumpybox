import os

import pyblish.api


class ValidateNukeGroupNode(pyblish.api.InstancePlugin):
    """Validates group node.

    Ensures none of the groups content is locally stored.
    """

    order = pyblish.api.ValidatorOrder
    optional = True
    families = ["gizmo", "lut"]
    label = "Group Node"
    hosts = ["nuke"]

    def process(self, instance):

        for node in instance[0].nodes():

            # Skip input and output nodes
            if node.Class() in ["Input", "Output"]:
                continue

            # Get file path
            file_path = ""
            if node.Class() == "Vectorfield":
                file_path = node["vfield_file"].getValue()
            if node.Class() == "Read":
                file_path = node["file"].getValue()

            # Validate file path to not be local
            # Windows specifc
            msg = "Node \"{0}\" in group \"{1}\"".format(
                node["name"].getValue(), instance[0]["name"].getValue()
            )
            msg += ", has a local file path: \"{0}\"".format(file_path)
            assert "c:" != os.path.splitdrive(file_path)[0].lower(), msg
