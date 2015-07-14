import pymel
import pyblish.api


@pyblish.api.log
class ValidateShading(pyblish.api.Validator):
    """"""

    families = ['scene']

    def process(self, instance):

        sgs = pymel.core.ls(type='shadingEngine')

        msg = 'Default lambert not on all nodes. Please assign "lambert1",'
        msg += ' and used Hypershade > Edit > Delete Unused Nodes.'
        assert len(sgs) == 2, msg
