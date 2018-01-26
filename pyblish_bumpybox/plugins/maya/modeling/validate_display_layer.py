from pyblish import api
from pyblish_bumpybox import inventory


class RepairDisplayLayerAction(api.Action):

    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):
        import pymel

        for layer in pymel.core.ls(type='displayLayer'):
            try:
                pymel.core.delete(layer)
            except:
                pass


class ValidateDisplayLayer(api.ContextPlugin):
    """ Ensure no displays layers are present in the scene """

    order = inventory.get_order(__file__, "ValidateDisplayLayer")
    optional = True
    label = 'Display Layers'
    actions = [RepairDisplayLayerAction]

    def process(self, context):
        """Process all the nodes in the instance """
        import pymel

        layers = []
        for layer in pymel.core.ls(type='displayLayer'):
            # skipping references
            if pymel.core.PyNode(layer).isReferenced():
                return

            if layer.name() != 'defaultLayer':
                layers.append(layer)

        assert not layers, 'Scene has displayLayers: %s' % layers
