import pyblish.api
import maya.cmds as cmds
import pymel


class ValidateConstructionHistory(pyblish.api.Validator):
    """ Ensure no construction history exists on the nodes in the instance """

    families = ['scene']
    optional = True
    label = 'Modeling - Construction History'

    def process(self, instance):
        """Process all the nodes in the instance """

        check = True

        for node in cmds.ls(type='transform'):
            # skipping references
            if not pymel.core.PyNode(node).isReferenced():

                history = cmds.listHistory(node, pruneDagObjects=True)
                if history:
                    for h in history:
                        if not pymel.core.PyNode(h).isReferenced():
                            msg = 'Node "%s" has construction' % node
                            msg += ' history: %s' % h
                            self.log.error(msg)
                            check = False


        assert check, 'Nodes in the scene has construction history.'
