import pyblish.api


class BumpyboxHoudiniValidateGeometry(pyblish.api.InstancePlugin):
    """ Validates that the SOP path is set. """

    families = ["geometry"]
    order = pyblish.api.ValidatorOrder
    label = "Geometry"
    hosts = ["houdini"]

    def process(self, instance):

        node = instance[0]

        msg = "No SOP path specified for node \"{0}\"."
        assert node.parm("soppath").eval(), msg.format(node.name())
