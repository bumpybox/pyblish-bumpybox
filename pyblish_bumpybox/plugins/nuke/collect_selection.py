from pyblish_bumpybox import plugin


class CollectSelection(plugin.ContextPlugin):
    """Collect selection."""

    order = plugin.CollectorOrder - 0.1
    label = "Selection"
    hosts = ["nuke"]
    targets = ["default", "process"]

    def process(self, context):
        import nuke
        context.data["selection"] = nuke.selectedNodes()
