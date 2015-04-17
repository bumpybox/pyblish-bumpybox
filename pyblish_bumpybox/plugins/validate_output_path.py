import os

import pyblish.api


@pyblish.api.log
class ValidateOutputPath(pyblish.api.Validator):
    """Validates that the output directory for the write nodes exists"""

    families = ['writeNode', 'prerenders']
    hosts = ['nuke']
    version = (0, 1, 0)

    def process_instance(self, instance):
        path = os.path.dirname(instance[0]['file'].value())

        if not os.path.exists(path):
            name = instance[0].name()
            msg = 'Output directory for %s doesn\'t exists' % name

            raise ValueError(msg)

    def repair_instance(self, instance):
        """Auto-repair creates the output directory"""
        path = os.path.dirname(instance[0]['file'].value())

        if not os.path.exists(path):
            os.makedirs(path)
