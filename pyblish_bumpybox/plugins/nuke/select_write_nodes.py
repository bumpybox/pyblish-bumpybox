import nuke

import pyblish.api


@pyblish.api.log
class SelectWriteNodes(pyblish.api.Selector):
    """
    Collects all write nodes as instances.
    """

    hosts = ['nuke']
    version = (0, 1, 0)

    def process_context(self, context):

        for node in nuke.allNodes():
            if node.Class() == 'Write':
                instance = context.create_instance(name=node.name())

                #instance.add(node)

                instance.set_data('family', value='Write Nodes')
