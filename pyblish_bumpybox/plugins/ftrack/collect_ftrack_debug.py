import logging

import pyblish.api


class CollectFtrackDebug(pyblish.api.ContextPlugin):
    """ Disable the debug messages from the ftrack api. """

    order = pyblish.api.CollectorOrder
    label = "Debug"

    def process(self, context):

        for log in logging.Logger.manager.loggerDict.keys():
            if "ftrack" in log:
                logging.getLogger(log).setLevel(logging.INFO)
