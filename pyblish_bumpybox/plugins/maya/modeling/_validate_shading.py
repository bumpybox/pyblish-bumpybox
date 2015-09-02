import pymel
import pyblish.api


class ValidateShading(pyblish.api.Validator):
    """"""

    families = ['scene']
    optional = True
    label = 'Modeling - Shading'

    def process(self, instance):

        sgs = pymel.core.ls(type='shadingEngine')

        msg = 'Default lambert not on all nodes. Please assign "lambert1",'
        msg += ' and used Hypershade > Edit > Delete Unused Nodes.'
        assert len(sgs) == 2, msg
