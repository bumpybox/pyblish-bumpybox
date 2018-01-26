from pyblish import api


class ValidateHierarchy(api.InstancePlugin):
    """ Ensures a flat hierarchy """

    order = api.ValidatorOrder
    families = ["mayaAscii", "mayaBinary", "alembic"]
    label = "Hierarchy"
    optional = True

    def process(self, instance):

        check = True
        for node in instance[0].members():
            if node.getParent():
                msg = "\"%s\" is parented to \"%s\"" % (node, node.getParent())
                msg += " Please unparent %s" % node
                self.log.error(msg)
                check = False

        assert check, "Wrong hierarchy in the scene."
