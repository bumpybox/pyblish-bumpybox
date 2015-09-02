import os
import platform

import pyblish.api


@pyblish.api.log
class ValidateDeadlineOutputLocation(pyblish.api.Validator):
    """Validates whether the output is local or networked"""

    families = ['deadline.render']
    optional = True
    label = 'Output Location'

    def process(self, instance):
        # checking output
        path = instance.data('deadlineData')['job']['OutputFilename0']
        path = os.path.dirname(path)
        mount = self.find_mount_point(path)
        if platform.system() == 'Windows':
            if 'c' in mount.lower():
                msg = 'Output path is not a network path: %s' % path
                raise ValueError(msg)

    def find_mount_point(self, path):
        path = os.path.abspath(path)
        while not os.path.ismount(path):
            path = os.path.dirname(path)
        return path
