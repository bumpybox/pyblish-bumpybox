import os

import pyblish.api


class CollectCelActionSceneVersion(pyblish.api.Collector):
    """
    """

    def process(self, context):

        path = context.data('kwargs')['data']['scene']
        v = int(os.path.splitext(path)[0].split('_')[-1])
        context.set_data('version', value=v)
