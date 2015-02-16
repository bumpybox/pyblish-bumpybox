import re
import os

import pyblish.api

class ValidateFilename(pyblish.api.Validator):
    """
    """

    families = ['filename']
    hosts = ['maya', 'modo']
    version = (0, 1, 0)

    pattern = re.compile('(.+)\.([a-z]+)\.([v])([0-9]{3})\.([a-z]+)')
    def process_context(self, context):
        """
        """
        name = os.path.basename(context.data('current_file'))
        if not self.pattern.match(name):
            err = ValueError('Filename incorrect!')
            raise err
