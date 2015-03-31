import os

import nuke
import pyblish.api


@pyblish.api.log
class SelectFileName(pyblish.api.Selector):
    """Selects version items"""

    hosts = ['nuke']
    version = (0, 1, 0)

    def process_context(self, context):

        current_file = nuke.root().name()
        basename = os.path.basename(current_file)

        instance = context.create_instance(name='Nuke Script and Write Nodes')
        instance.set_data('family', value='versionPaths')

        instance.set_data('path', value=current_file)

        for node in nuke.allNodes():
            if node.Class() == 'Write' and not node['disable'].getValue():
                instance.add(node)
