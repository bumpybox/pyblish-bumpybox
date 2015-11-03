import nuke
import pyblish.api


class Collect3dNodes(pyblish.api.Collector):
    """
    """

    def process(self, context):
        for node in nuke.allNodes():

            if node.Class() == 'Camera2':
                instance = context.create_instance(name=node.name())
                instance.set_data('family', value='camera')
                instance.add(node)

            if node.Class() == 'Axis2':
                instance = context.create_instance(name=node.name())
                instance.set_data('family', value='axis')
                instance.add(node)
