import os

import pyblish.api
import pyseq

@pyblish.api.log
class ValidateMissingFrames(pyblish.api.Validator):
    """
    """

    families = ['png']

    def process(self, instance):
        seq = pyseq.get_sequences(os.path.dirname(instance.data('path')))[0]

        msg = 'Image sequence is missing: %s' % seq.missing()
        assert not seq.missing(), msg
