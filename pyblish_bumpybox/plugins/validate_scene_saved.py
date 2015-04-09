import nuke

import pyblish.api


@pyblish.api.log
class ValidateSceneSaved(pyblish.api.Validator):
    """Validates whether the scene is saved"""

    families = ['*']
    hosts = ['nuke']
    version = (0, 1, 0)

    def process_context(self, context):

        root = nuke.Root()
        if root.modified():
            msg = 'Scene has not been saved since modifying.'
            raise ValueError(msg)

    def repair_context(self, context):
        """Saves the script
        """
        nuke.scriptSave()
