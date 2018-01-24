import pyblish.api


class CollectFramerate(pyblish.api.ContextPlugin):
    """Collect framerate."""

    order = pyblish.api.CollectorOrder
    label = "Framerate"
    hosts = ["nuke", "nukeassist"]
    targets = ["default", "process"]

    def process(self, context):
        import nuke

        context.data["framerate"] = nuke.root()["fps"].getValue()
