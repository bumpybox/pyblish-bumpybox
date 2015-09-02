import os

import pyblish.api
import ftrack


class ExtractDeadline(pyblish.api.Extractor):

    label = 'Split Levels'
    publish = False
    families = ['render']
    optional = True
    order = pyblish.api.Extractor.order - 0.2

    def process(self, instance, context):

        instance.set_data('levelSplit', value=True)
