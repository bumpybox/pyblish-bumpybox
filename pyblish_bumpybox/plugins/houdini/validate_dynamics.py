from pyblish import api
from pyblish_bumpybox import inventory


class ValidateDynamics(api.ContextPlugin):
    """ Validates that the DOP path is set. """

    families = ["dynamics"]
    order = inventory.get_order(__file__, "ValidateDynamics")
    label = "Dynamics"
    hosts = ["houdini"]

    def process(self, instance):

        node = instance[0]

        msg = "No DOP path specified for node \"{0}\"."
        assert node.parm("doppath").eval(), msg.format(node.name())
