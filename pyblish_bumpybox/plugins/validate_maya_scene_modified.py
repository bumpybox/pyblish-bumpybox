import maya
import pyblish.api


@pyblish.api.log
class ValidateMayaSceneModified(pyblish.api.Validator):
    """ Validates whether the scene has been saved since modifying
    """

    families = ['scene']
    hosts = ['maya']
    version = (0, 1, 0)
    label = 'Scene Saved'

    def process(self, instance):

        msg = 'Scene has not been saved since modifying.'
        assert not maya.cmds.file(q=True, mf=True), msg

    def repair(self, instance):
        """ Saves the scene
        """
        maya.cmds.file(s=True)
