import os

import pyblish.api
import nuke


@pyblish.api.log
class SelectWorkfile(pyblish.api.Selector):
    """"""

    hosts = ['nuke']
    version = (0, 1, 0)

    def process_context(self, context):
        """Todo, inject the current working file"""
        current_file = nuke.root().name()

        normalised = os.path.normpath(current_file)

        instance = context.create_instance(name=os.path.basename(normalised))

        instance.set_data('family', value='workFile')

        instance.set_data('path', value=normalised)
