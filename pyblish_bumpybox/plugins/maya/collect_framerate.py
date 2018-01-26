from pyblish_bumpybox import plugin


class CollectFramerate(plugin.ContextPlugin):
    """Collect the frame rate."""

    order = plugin.CollectorOrder - 0.5
    label = "Framerate"
    hosts = ["maya"]
    targets = ["default", "process"]

    def process(self, context):
        import pymel.core
        options = {"pal": 25, "game": 15, "film": 24, "ntsc": 30, "show": 48,
                   "palf": 50, "ntscf": 60}

        option = pymel.core.general.currentUnit(q=True, t=True)

        context.data["framerate"] = options[option]
