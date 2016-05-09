import pyblish.api
import nuke


class ValidateFrameRate(pyblish.api.Validator):
    """"""

    families = ['deadline.render']
    label = 'Frame Rate'
    optional = True

    def process(self, context):

        msg = "Frame rate can't be zero."
        assert nuke.root()['fps'].value() != 0, msg
