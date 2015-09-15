import pyblish.api
import pymel


class ValidateHierarchy(pyblish.api.Validator):
    """ Ensures a flat hierarchy """

    families = ['geometry']
    label = 'Modeling - Hierarchy'

    def process(self, instance):

        node = instance[0]
        if node.getParent():

            msg = '"%s" is parented to "%s"' % (node, node.getParent())
            msg += ' Please unparent %s' % node
            assert check, msg
