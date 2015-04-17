import os

import pyblish.api


@pyblish.api.log
class ValidatePrerendersOutput(pyblish.api.Validator):
    """Validates that the output directory for the write nodes exists"""

    families = ['prerenders']
    hosts = ['nuke']
    version = (0, 1, 0)

    def process_instance(self, instance):
        path = os.path.dirname(instance[0]['file'].value())

        if 'output' not in path:
            name = instance[0].name()
            msg = 'Output directory for %s is not in an "output" folder.' % name

            raise ValueError(msg)
