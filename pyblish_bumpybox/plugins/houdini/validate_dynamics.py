from pyblish_bumpybox import plugin


class ValidateDynamics(plugin.InstancePlugin):
    """ Validates that the DOP path is set. """

    families = ["dynamics"]
    order = plugin.ValidatorOrder
    label = "Dynamics"
    hosts = ["houdini"]

    def process(self, instance):

        node = instance[0]

        msg = "No DOP path specified for node \"{0}\"."
        assert node.parm("doppath").eval(), msg.format(node.name())
