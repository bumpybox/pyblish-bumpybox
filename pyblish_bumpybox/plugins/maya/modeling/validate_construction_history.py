import pyblish.api
import maya.cmds as cmds


class ValidateConstructionHistory(pyblish.api.Validator):
    """ Ensure no construction history exists on the nodes in the instance """

    families = ['scene']

    def process(self, instance):
        """Process all the nodes in the instance """

        check = True
        for node in cmds.ls(type='transform'):
            history = cmds.listHistory(node, pruneDagObjects=True)
            if cmds.listHistory(node, pruneDagObjects=True):
                msg = 'Node "%s" has construction history: %s' % (node, history)
                self.log.error(msg)
                check = False

        assert check, 'Nodes in the scene has construction history.'
