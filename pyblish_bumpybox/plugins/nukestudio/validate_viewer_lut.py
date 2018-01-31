from pyblish import api
from pyblish_bumpybox import inventory


class ValidateViewerLut(api.ContextPlugin):
    """Validate viewer lut in NukeStudio is the same as in Nuke."""

    order = inventory.get_order(__file__, "ValidateViewerLut")
    label = "Viewer LUT"
    hosts = ["nukestudio"]
    optional = True

    def process(self, context):
        import nuke
        import hiero.core

        nuke_lut = nuke.ViewerProcess.node()["current"].value()
        nukestudio_lut = hiero.core.projects()[0].lutSettingViewer()

        msg = "Viewer LUT can only be sRGB"
        assert nukestudio_lut == "sRGB", msg

        msg = "Viewer LUTs in NukeStudio and Nuke does not match."
        assert nuke_lut == nukestudio_lut, msg
