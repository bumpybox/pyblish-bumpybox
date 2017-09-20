import nuke

import pyblish.api


class CollectNukeFramerate(pyblish.api.ContextPlugin):
    """Collect framerate."""

    order = pyblish.api.CollectorOrder
    label = "Framerate"
    hosts = ["nuke"]
    targets = ["default", "process"]

    def process(self, context):

        context.data["framerate"] = nuke.root()["fps"].getValue()
