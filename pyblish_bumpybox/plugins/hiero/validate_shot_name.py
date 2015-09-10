import re

import pyblish.api
import hiero


class ValidateShotName(pyblish.api.Validator):
    """ Validates the shot name to end with something similar to 'sh###'
    """

    families = ['ftrack.trackItem', 'transcode_png.trackItem',
                                                'transcode_prores.trackItem']
    label = 'Shot Name'

    def process(self, instance, context):

        check = False
        item = instance[0]

        naming = r'([a-z]{1,2}[0-9]{3}\b)'
        if re.findall(naming, item.name()):
            check = True

        item_name = '%s: %s' % (item.parent().name(), item.name())
        msg = '"%s" has incorrect naming' % item_name
        assert check, msg
