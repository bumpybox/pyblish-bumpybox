from pyblish import api
from pyblish_bumpybox import inventory


class ValidateMantraCamera(api.InstancePlugin):
    """ Validates that the camera for mantra nodes exists. """

    families = ["mantra"]
    order = inventory.get_order(__file__, "ValidateMantraCamera")
    label = "Mantra Camera"
    hosts = ["houdini"]

    def process(self, instance):
        import hou

        node = instance[0]
        camera = node.parm("camera").eval()

        msg = "Camera \"{0}\" does not exist."
        msg += "\nMake sure mantra points to an existing camera."
        assert hou.node(node.parm("camera").eval()), msg.format(camera)
