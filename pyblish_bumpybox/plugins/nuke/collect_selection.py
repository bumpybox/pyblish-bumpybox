from pyblish import api
from pyblish_bumpybox import inventory


class CollectSelection(api.ContextPlugin):
    """Collect selection."""

    order = inventory.get_order(__file__, "CollectSelection")
    label = "Selection"
    hosts = ["nuke"]
    targets = ["default", "process"]

    def process(self, context):
        import nuke
        context.data["selection"] = nuke.selectedNodes()
