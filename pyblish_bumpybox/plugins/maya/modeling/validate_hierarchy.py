import pyblish.api
import pymel


class ValidateHierarchy(pyblish.api.Validator):
    """ Ensures a flat hierarchy """

    families = ['geometry']
    label = 'Hierarchy'

    def process(self, instance):

        check = True
        for node in instance:
            if node.getParent():
                msg = '"%s" is parented to "%s"' % (node, node.getParent())
                msg += ' Please unparent %s' % node
                self.log.error(msg)
                check = False

        assert check, 'Wrong hierarchy in the scene.'
