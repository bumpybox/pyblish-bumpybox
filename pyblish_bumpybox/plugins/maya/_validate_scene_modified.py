import maya
import pyblish.api


@pyblish.api.log
class ValidateSceneModified(pyblish.api.Validator):
    """ Validates whether the scene has been saved since modifying
    There is a case where the saving of the scene crashes Pyblish,
    so no repair is in place for this validator:s
    """

    families = ['scene']
    hosts = ['maya']
    label = 'Scene Modified'
    optional = True

    def process(self, instance):

        msg = 'Scene has not been saved since modifying.'
        assert not maya.cmds.file(q=True, mf=True), msg
