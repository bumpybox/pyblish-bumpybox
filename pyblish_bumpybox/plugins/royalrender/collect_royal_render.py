import pyblish.api


class CollectNukeWritesRoyalRender(pyblish.api.ContextPlugin):
    """Collect all write nodes."""

    order = pyblish.api.CollectorOrder + 0.1
    label = "Writes Royal Render"
    hosts = ["nuke"]
    targets = ["processing.royalrender"]

    def process(self, context):

        for item in context.data["instances"]:
            instance = context.create_instance(item.data["name"])
            for key, value in item.data.iteritems():
                instance.data[key] = value

            instance.data["label"] += " - royalrender"
            instance.data["families"].append("royalrender")
            for node in item:
                instance.add(node)
