from pyblish import api
from pyblish_bumpybox import inventory


class ExtractGroup(api.ContextPlugin):
    """ Extract gizmos from group nodes. """

    order = inventory.get_order(__file__, "ExtractGroup")
    optional = True
    families = ["gizmo", "lut"]
    label = "Group"
    hosts = ["nuke", "nukeassist"]

    def process(self, instance):
        import os

        import nuke

        if not instance.data["publish"]:
            return

        file_path = instance.data["output_path"]
        directory = os.path.dirname(file_path)

        # Create workspace if necessary
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Export gizmo
        # Deselect all nodes
        for node in nuke.selectedNodes():
            node["selected"].setValue(False)

        instance[0]["selected"].setValue(True)

        nuke.nodeCopy(file_path)

        data = ""
        with open(file_path, "r") as f:
            data = f.read()

        data = data.replace("set cut_paste_input [stack 0]\n", "")
        data = data.replace("push $cut_paste_input\n", "")
        data = data.replace("Group {\n", "Gizmo {\n")

        with open(file_path, "w") as f:
            f.write(data)
