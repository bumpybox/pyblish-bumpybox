import pyblish.api
import nuke


class ValidateNukeFrameRate(pyblish.api.ContextPlugin):
    """ Validate frame rate to ensure, its never zero. """

    order = pyblish.api.ValidatorOrder
    families = ["write"]
    label = "Frame Rate"
    optional = True

    def process(self, context):

        msg = "Frame rate can't be zero."
        assert nuke.root()["fps"].value() != 0, msg
