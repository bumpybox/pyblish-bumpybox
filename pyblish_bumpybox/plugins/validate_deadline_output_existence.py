import os

import pyblish.api


@pyblish.api.log
class ValidateDeadlineOutputExistence(pyblish.api.Validator):
    """Validates that the output directory for the write nodes exists"""

    families = ['deadline.render']
    hosts = ['*']
    version = (0, 1, 0)
    label = 'Output Existence'

    def process(self, instance):
        path = instance.data('deadlineJobData')['OutputFilename0']
        path = os.path.dirname(path)

        if not os.path.exists(path):
            msg = 'Output directory for %s doesn\'t exists: %s' % (instance,
                                                                   path)
            raise ValueError(msg)

    def repair(self, instance):
        """Auto-repair creates the output directory"""
        path = instance.data('deadlineJobData')['OutputFilename0']
        path = os.path.dirname(path)

        if not os.path.exists(path):
            os.makedirs(path)
