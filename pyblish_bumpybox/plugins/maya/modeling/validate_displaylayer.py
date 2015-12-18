import pyblish.api
import pymel


class ValidateDisplaylayer(pyblish.api.Validator):
    """ Ensure no construction history exists on the nodes in the instance """

    families = ['scene']
    optional = True
    label = 'Display Layers'

    def process(self, instance):
        """Process all the nodes in the instance """

        layers = []
        for layer in pymel.core.ls(type='displayLayer'):
            # skipping references
            if pymel.core.PyNode(layer).isReferenced():
                return

            if layer.name() != 'defaultLayer':
                layers.append(layer)

        assert not layers, 'Scene has displayLayers: %s' % layers

    def repair(self, instance):

        for layer in pymel.core.ls(type='displayLayer'):
            try:
                pymel.core.delete(layer)
            except:
                pass
