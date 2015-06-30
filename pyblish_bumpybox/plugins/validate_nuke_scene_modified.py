import nuke

import pyblish.api


@pyblish.api.log
class ValidateNukeSceneModified(pyblish.api.Validator):
    """ Validates whether the scene has been saved since modifying
    """

    families = ['scene', 'scene.old']
    hosts = ['nuke']
    version = (0, 1, 0)
    label = 'Scene Saved'

    def process(self, instance):

        root = nuke.Root()
        if root.modified():
            msg = 'Scene has not been saved since modifying.'
            raise ValueError(msg)

    def repair(self, instance):
        """ Saves the nuke script
        """
        nuke.scriptSave()
