from pyblish import api
from pyblish_bumpybox import inventory


class CollectFramerate(api.ContextPlugin):
    """Collect the frame rate."""

    order = inventory.get_order(__file__, "CollectFramerate")
    label = "Framerate"
    hosts = ["maya"]
    targets = ["default", "process"]

    def process(self, context):
        import pymel.core
        options = {"pal": 25, "game": 15, "film": 24, "ntsc": 30, "show": 48,
                   "palf": 50, "ntscf": 60}

        option = pymel.core.general.currentUnit(q=True, t=True)

        context.data["framerate"] = options[option]
