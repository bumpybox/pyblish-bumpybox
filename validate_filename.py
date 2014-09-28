import re
import os

import pyblish.api

class ValidateFilename(pyblish.api.Validator):
    """
    """

    families = ['filename']
    hosts = ['maya']
    version = (0, 1, 0)

    pattern = re.compile('(.+)\.([a-z]+)\.([v])([0-9]{3})\.([a-z]+)')
    def process_instance(self, instance):
        """
        """
        self.log.info('Processing instance')
        self.log.info(instance)
        name = os.path.basename(instance.data('current_file'))
        if not self.pattern.match(name):
            err = ValueError('Filename incorrect!')
            raise err

    def process_context(self, context):
        self.log.info('Processing context')
        for instance in context:
            self.log.info(instance)
