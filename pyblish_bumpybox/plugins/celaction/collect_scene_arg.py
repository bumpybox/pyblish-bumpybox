import os
import sys

import pyblish.api


pyblish.api.register_host('celaction')


class CollectSceneArg(pyblish.api.Collector):
    """"""

    order = pyblish.api.Collector.order - 0.05

    def process(self, context):

        path = context.data('kwargs')['data']['scene']
        context.set_data('currentFile', value=path)
