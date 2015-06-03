import nuke

import pyblish.api


@pyblish.api.log
class ValidateSceneModifiedNuke(pyblish.api.Validator):
    """ Validates whether the scene has been saved since modifying
    """

    families = ['scene']
    hosts = ['nuke']
    version = (0, 1, 0)

    def process_instance(self, instance):

        root = nuke.Root()
        if root.modified():
            msg = 'Scene has not been saved since modifying.'
            raise ValueError(msg)

    def repair_instance(self, instance):
        """ Saves the nuke script
        """
        nuke.scriptSave()
