from pyblish import api


class CollectFramerate(api.ContextPlugin):
    """Collect framerate."""

    order = api.CollectorOrder
    label = "Framerate"
    hosts = ["nuke", "nukeassist"]
    targets = ["default", "process"]

    def process(self, context):
        import nuke

        context.data["framerate"] = nuke.root()["fps"].getValue()
