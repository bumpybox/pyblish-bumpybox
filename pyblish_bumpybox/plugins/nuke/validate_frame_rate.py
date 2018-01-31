from pyblish import api
from pyblish_bumpybox import inventory


class ValidateFrameRate(api.ContextPlugin):
    """ Validate frame rate to ensure, its never zero. """

    order = inventory.get_order(__file__, "ValidateFrameRate")
    families = ["write"]
    label = "Frame Rate"
    optional = True
    targets = ["default", "process"]

    def process(self, context):
        import nuke
        msg = "Frame rate can't be zero."
        assert nuke.root()["fps"].value() != 0, msg
