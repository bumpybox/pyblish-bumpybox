import pymel.core
import pyblish.api


class ValidateUnknownNodes(pyblish.api.Validator):
    """
    """

    families = ['scene']
    label = 'Unknown Nodes'

    def process(self, instance):

        nodes = []
        for node in pymel.core.ls(type='unknown'):
            if not node.isReferenced():
                nodes.append(node)

        msg = 'Unknown nodes in scene: {0}'.format(nodes)
        assert not nodes, msg

    def repair(self, instance):

        pymel.core.delete(pymel.core.ls(type='unknown'))
