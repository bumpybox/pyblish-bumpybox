from pyblish_bumpybox import plugin


class CollectFramerate(plugin.ContextPlugin):
    """Collect framerate."""

    order = plugin.CollectorOrder
    label = "Framerate"
    hosts = ["nuke", "nukeassist"]
    targets = ["default", "process"]

    def process(self, context):
        import nuke

        context.data["framerate"] = nuke.root()["fps"].getValue()
