import nuke
import pyblish.api
import clique


class CollectNukeWrites(pyblish.api.ContextPlugin):
    """Collect all write nodes."""

    order = pyblish.api.CollectorOrder
    label = "Writes"
    hosts = ["nuke"]

    def process(self, context):

        # Get remote nodes
        remote_nodes = []
        for node in nuke.allNodes():
            if node.Class() == "BackdropNode":
                if node.name().lower().startswith("remote"):
                    remote_nodes.extend(node.getNodes())

        remote_nodes = list(set(remote_nodes))

        # creating instances per write node
        for node in nuke.allNodes():
            if node.Class() != "Write":
                continue

            # Determine output type
            output_type = "img"
            if node["file_type"].value() == "mov":
                output_type = "mov"

            # Determine processing location from backdrops
            process_place = "local"
            if node in remote_nodes:
                process_place = "remote"

            # Create instance
            instance = context.create_instance(name=node.name())
            instance.data["families"] = ["write", process_place, output_type]
            instance.data["family"] = output_type
            instance.add(node)

            label = "{0} - write - {1}"
            instance.data["label"] = label.format(node.name(), process_place)

            instance.data["publish"] = bool(not node["disable"].getValue())

            # Get frame range
            start_frame = int(nuke.root()["first_frame"].getValue())
            end_frame = int(nuke.root()["last_frame"].getValue())
            if node["use_limit"].getValue():
                start_frame = int(node["first"].getValue())
                end_frame = int(node["last"].getValue())

            # Add collection
            collection = None
            try:
                path = ""
                if nuke.filename(node):
                    path = nuke.filename(node)
                path += " [{0}-{1}]".format(start_frame, end_frame)
                collection = clique.parse(path)
            except Exception as e:
                self.log.warning(e)

            instance.data["collection"] = collection
