import logging

import pyblish.api


class DisableFtrackDebugMessages(pyblish.api.ContextPlugin):
    """ Disable the debug messages from the ftrack api. """

    order = pyblish.api.CollectorOrder

    def process(self, context):

        for log in logging.Logger.manager.loggerDict.keys():
            if "ftrack" in log:
                logging.getLogger(log).setLevel(logging.INFO)
