import nuke
import pyblish.api


class CollectReadNodes(pyblish.api.Collector):
    """
    """

    def process(self, context):
        for node in nuke.allNodes():

            if node.Class() == 'Read':
                instance = context.create_instance(name=node.name())
                instance.set_data('family', value='read')
                instance.add(node)
