import pyblish.api
import pymel


class ValidateHierarchy(pyblish.api.Validator):
    """ Ensures a flat hierarchy """

    families = ['scene']
    optional = True
    label = 'Modeling - Hierarchy'

    def process(self, instance):

        check = True
        for node in pymel.core.ls(type='mesh'):
            if node.getParent().getParent():
                msg = '"%s" is parented to "%s"' % (node, node.getParent())
                self.log.error(msg)
                check = False

        msg = 'Some nodes are not direct a child of the world.'
        msg += ' Please unparent all transforms.'
        assert check, msg
