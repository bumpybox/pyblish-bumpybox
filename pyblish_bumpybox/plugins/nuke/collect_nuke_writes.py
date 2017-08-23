import nuke
import pyblish.api
import clique


class CollectNukeWrites(pyblish.api.ContextPlugin):
    """Collect all write nodes."""

    order = pyblish.api.CollectorOrder
    label = "Writes"
    hosts = ["nuke"]
    targets = ["default", "processing"]

    def process(self, context):

        instances = context.data.get("instances", [])
        # creating instances per write node
        for node in nuke.allNodes():
            if node.Class() != "Write":
                continue

            # Determine output type
            output_type = "img"
            if node["file_type"].value() == "mov":
                output_type = "mov"

            # Create instance
            instance = pyblish.api.Instance(node.name())
            instance.data["families"] = ["write", output_type]
            instance.data["family"] = output_type
            instance.add(node)

            instance.data["label"] = "{0} - write".format(node.name())

            instance.data["publish"] = not node["disable"].getValue()

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

            instances.append(instance)

        context.data["instances"] = instances


class CollectNukeWritesLocal(pyblish.api.ContextPlugin):
    """Collect all local processing write instances."""

    order = CollectNukeWrites.order + 0.01
    label = "Writes Local"
    hosts = ["nuke"]
    targets = ["processing.local"]

    def process(self, context):

        for item in context.data["instances"]:
            instance = context.create_instance(item.data["name"])
            for key, value in item.data.iteritems():
                instance.data[key] = value

            instance.data["label"] += " - local"
            instance.data["families"].append("local")
            for node in item:
                instance.add(node)
