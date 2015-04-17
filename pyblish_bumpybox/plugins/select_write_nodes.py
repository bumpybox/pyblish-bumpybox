import nuke
import pyblish.api


@pyblish.api.log
class SelectWriteNodes(pyblish.api.Selector):
    """Selects all write nodes"""

    hosts = ['nuke']
    version = (0, 1, 0)

    def upstream_nodes(self, node, results=[]):
        if node.dependencies():
            results.extend(node.dependencies())
            for n in node.dependencies():
                return self.upstream_nodes(n)

        return results

    def process_context(self, context):

        write_nodes = []
        for node in nuke.allNodes():
            if node.Class() == 'Write' and not node['disable'].getValue():
                write_nodes.append(node)

        last_write_node = None
        for node in write_nodes:
            last_write_node = set(write_nodes) - set(self.upstream_nodes(node))

        prerender_write_nodes = set(write_nodes) - set(last_write_node)
        final_write_node = list(last_write_node)[0]

        instance = context.create_instance(name=final_write_node.name())
        instance.set_data('family', value='writeNode')
        instance.add(final_write_node)

        for node in list(prerender_write_nodes):
            instance = context.create_instance(name=node.name())
            instance.set_data('family', value='prerenders')
            instance.add(node)
