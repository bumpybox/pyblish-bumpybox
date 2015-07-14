import pyblish.api
import maya.cmds as cmds


class ValidateDisplaylayer(pyblish.api.Validator):
    """ Ensure no construction history exists on the nodes in the instance """

    families = ['scene']

    def process(self, instance):
        """Process all the nodes in the instance """

        layers = []
        for layer in cmds.ls(type='displayLayer'):
            if layer != 'defaultLayer':
                layers.append(layer)

        assert not layers, 'Scene has displayLayers: %s' % layers
