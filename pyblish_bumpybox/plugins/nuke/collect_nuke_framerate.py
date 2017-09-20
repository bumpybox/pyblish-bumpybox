import nuke

import pyblish.api


class CollectNukeFramerate(pyblish.api.ContextPlugin):
    """Collect framerate."""

    order = pyblish.api.CollectorOrder
    label = "Nuke Framerate"
    hosts = ["nuke"]

    def process(self, context):

        context.data["framerate"] = nuke.root()["fps"].getValue()
