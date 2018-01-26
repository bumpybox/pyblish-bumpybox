from pyblish import api


class CollectSelection(api.ContextPlugin):
    """Collect selection."""

    order = api.CollectorOrder - 0.1
    label = "Selection"
    hosts = ["nuke"]
    targets = ["default", "process"]

    def process(self, context):
        import nuke
        context.data["selection"] = nuke.selectedNodes()
