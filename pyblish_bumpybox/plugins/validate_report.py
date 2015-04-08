import os
import time
import json

import pyblish.api

@pyblish.api.log
class ReportValidator(pyblish.api.Validator):
    families = ['writeNode', 'versionPaths', 'versionPaths']
    hosts = ['nuke']
    version = (0, 1, 0)
    order = pyblish.api.Validator.order + 0.5

    def process_context(self, context):
        # runs once, always.
        if not context.data('failedPlugins'):
              return

        data = str(context.data("failedPlugins"))
        current_file = context.data('current_file')
        user = context.data('user')
        date_format = "%Y%d%m_%H%M%S"
        filename = time.strftime(date_format) + '.log'

        path = os.path.join(r'K:\tools\Pyblish\reports', str(user))

        if not os.path.exists(path):
            os.mkdir(path)

        path = os.path.join(path, filename)
        self.log.info(data)
        with open(path, 'w') as outfile:
            json.dumps(data, outfile, indent=4)
