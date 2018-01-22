import pyblish.api


class ValidateNukeFrameRate(pyblish.api.ContextPlugin):
    """ Validate frame rate to ensure, its never zero. """

    order = pyblish.api.ValidatorOrder
    families = ["write"]
    label = "Frame Rate"
    optional = True
    targets = ["default", "process"]

    def process(self, context):
        import nuke
        msg = "Frame rate can't be zero."
        assert nuke.root()["fps"].value() != 0, msg
