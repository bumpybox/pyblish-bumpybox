from pyblish import api
from pyblish_bumpybox import inventory


class ValidateGeometry(api.ContextPlugin):
    """ Validates that the SOP path is set. """

    families = ["geometry"]
    order = inventory.get_order(__file__, "ValidateGeometry")
    label = "Geometry"
    hosts = ["houdini"]

    def process(self, instance):

        node = instance[0]

        msg = "No SOP path specified for node \"{0}\"."
        assert node.parm("soppath").eval(), msg.format(node.name())
