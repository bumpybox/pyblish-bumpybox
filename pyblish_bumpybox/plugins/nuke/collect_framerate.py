from pyblish import api
from pyblish_bumpybox import inventory


class CollectFramerate(api.ContextPlugin):
    """Collect framerate."""

    order = inventory.get_order(__file__, "CollectFramerate")
    label = "Framerate"
    hosts = ["nuke", "nukeassist"]
    targets = ["default", "process"]

    def process(self, context):
        import nuke

        context.data["framerate"] = nuke.root()["fps"].getValue()
