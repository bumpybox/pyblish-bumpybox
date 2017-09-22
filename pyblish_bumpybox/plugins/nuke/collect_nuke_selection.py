import nuke

import pyblish.api


class CollectNukeSelection(pyblish.api.ContextPlugin):
    """Collect selection."""

    order = pyblish.api.CollectorOrder - 0.1
    label = "Selection"
    hosts = ["nuke"]
    targets = ["default", "process"]

    def process(self, context):
        context.data["selection"] = nuke.selectedNodes()
