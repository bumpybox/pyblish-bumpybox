import os

import pyblish.api

import maya.cmds as cmds

@pyblish.api.log
class SelectFilename(pyblish.api.Selector):
    """
    """

    hosts = ['maya']
    version = (0, 1, 0)

    def process_context(self, context):
        """Todo, inject the current working file"""

        instance = context.create_instance(name='filename')
        
        instance.set_data(pyblish.api.config['identifier'], value='True')
        instance.set_data('families', value='filename')
        
        current_file = cmds.file(sceneName=True, query=True)

        # Maya returns forward-slashes by default
        normalised = os.path.normpath(current_file)

        instance.set_data('current_file', value=normalised)
