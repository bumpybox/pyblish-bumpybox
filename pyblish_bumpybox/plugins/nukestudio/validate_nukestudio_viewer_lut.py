import pyblish.api


class ValidateNukeStudioViewerLut(pyblish.api.ContextPlugin):
    """Validate viewer lut in NukeStudio is the same as in Nuke."""

    order = pyblish.api.ValidatorOrder
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
