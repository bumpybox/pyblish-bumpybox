import nuke
import pyblish.api

@pyblish.api.log
class ValidateCrop(pyblish.api.Validator):
    """Validates the existence of crop node before write node
    """

    families = ['deadline.render']
    hosts = ['nuke']
    version = (0, 1, 0)
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
