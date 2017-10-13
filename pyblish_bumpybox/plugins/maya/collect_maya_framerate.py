import pymel.core

import pyblish.api


class CollectMayaFramerate(pyblish.api.ContextPlugin):
    """Collect the frame rate."""

    order = pyblish.api.CollectorOrder - 0.5
    label = "Framerate"
    hosts = ["maya"]

    def process(self, context):

        options = {"pal": 25, "game": 15, "film": 24, "ntsc": 30, "show": 48,
                   "palf": 50, "ntscf": 60}

        option = pymel.core.general.currentUnit(q=True, t=True)

        context.data["framerate"] = options[option]
