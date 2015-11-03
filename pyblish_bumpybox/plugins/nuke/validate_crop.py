import nuke
import pyblish.api


class ValidateCrop(pyblish.api.Validator):
    """Validates the existence of crop node before write node
    """

    families = ['deadline.render']
    label = 'Crop Output'
    optional = True

    def process(self, instance):

        # skipping the call up project
        ftrack_data = instance.context.data('ftrackData')
        if ftrack_data['Project']['code'] == 'the_call_up':
            return

        node = nuke.toNode(str(instance))

        msg = "Couldn't find a crop node before %s" % instance
        assert node.dependencies()[0].Class() == 'Crop', msg

    def repair(self, instance):
        
        node = nuke.toNode(str(instance))
        input = node.input(0)

        crop = nuke.nodes.Crop(inputs=[node.input(0)])
        crop['box'].setValue(input.width(), 2)
        crop['box'].setValue(input.height(), 3)

        node.setInput(0, crop)
