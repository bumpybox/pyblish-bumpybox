import nuke
import pyblish.api


@pyblish.api.log
class SelectWriteNodes(pyblish.api.Selector):
    """Selects all write nodes"""

    hosts = ['nuke']
    version = (0, 1, 0)

    def process_context(self, context):

        for node in nuke.allNodes():
            if node.Class() == 'Write':
                instance = context.create_instance(name=node.name())
                instance.set_data('family', value='writeNode')
                instance.add(node)
