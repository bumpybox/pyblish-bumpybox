import pyblish.api
import pymel


class BumpyboxMayaModeligRepairDisplayLayer(pyblish.api.Action):

    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):

        for layer in pymel.core.ls(type='displayLayer'):
            try:
                pymel.core.delete(layer)
            except:
                pass


class BumpyboxMayaModelingValidateDisplaylayer(pyblish.api.ContextPlugin):
    """ Ensure no displays layers are present in the scene """

    order = pyblish.api.ValidatorOrder
    optional = True
    label = 'Display Layers'
    actions = [BumpyboxMayaModeligRepairDisplayLayer]

    def process(self, context):
        """Process all the nodes in the instance """

        layers = []
        for layer in pymel.core.ls(type='displayLayer'):
            # skipping references
            if pymel.core.PyNode(layer).isReferenced():
                return

            if layer.name() != 'defaultLayer':
                layers.append(layer)

        assert not layers, 'Scene has displayLayers: %s' % layers
