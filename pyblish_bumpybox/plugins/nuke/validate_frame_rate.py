from pyblish import api


class ValidateFrameRate(api.ContextPlugin):
    """ Validate frame rate to ensure, its never zero. """

    order = api.ValidatorOrder
    families = ["write"]
    label = "Frame Rate"
    optional = True
    targets = ["default", "process"]

    def process(self, context):
        import nuke
        msg = "Frame rate can't be zero."
        assert nuke.root()["fps"].value() != 0, msg
