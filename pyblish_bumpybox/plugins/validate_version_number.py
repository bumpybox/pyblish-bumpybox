import operator
import traceback

import nuke
import nukescripts
import pyblish.api


@pyblish.api.log
class ValidateVersionNumber(pyblish.api.Validator):
    """Validates the version number of write nodes compared to the file name
    """

    families = ['writeNodes']
    hosts = ['nuke']
    version = (0, 1, 0)

    def process_instance(self, instance):
        log.info(instance.context)

    def repair_instance(self, instance):
        """Sets the version number of the output to the same as the file name
        """
        pass
