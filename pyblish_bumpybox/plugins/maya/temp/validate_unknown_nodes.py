import pymel.core
import pyblish.api


class RepairUnknownNodes(pyblish.api.Action):

    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):

        pymel.core.delete(pymel.core.ls(type='unknown'))


class ValidateUnknownNodes(pyblish.api.Validator):
    """
    """

    families = ['scene']
    label = 'Unknown Nodes'
    actions = [RepairUnknownNodes]

    def process(self, context):

        nodes = []
        for node in pymel.core.ls(type='unknown'):
            if not node.isReferenced():
                nodes.append(node)

        msg = 'Unknown nodes in scene: {0}'.format(nodes)
        assert not nodes, msg
