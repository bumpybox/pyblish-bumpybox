import pyblish.api


class CollectFtrackFramerate(pyblish.api.ContextPlugin):
    """Collect framerate."""

    order = pyblish.api.CollectorOrder + 0.1
    label = "Ftrack Framerate"
    hosts = ["nuke"]

    def process(self, context):

        parent = context.data["ftrackTask"]["parent"]
        if "fps" in parent["custom_attributes"]:
            context.data["framerate"] = parent["custom_attributes"]["fps"]
