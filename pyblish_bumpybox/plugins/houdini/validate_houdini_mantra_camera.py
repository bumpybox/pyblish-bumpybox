import hou
import pyblish.api


class ValidateHoudiniMantraCamera(pyblish.api.InstancePlugin):
    """ Validates that the camera for mantra nodes exists. """

    families = ["mantra"]
    order = pyblish.api.ValidatorOrder
    label = "Mantra Camera"
    hosts = ["houdini"]

    def process(self, instance):

        node = instance[0]
        camera = node.parm("camera").eval()

        msg = "Camera \"{0}\" does not exist."
        msg += "\nMake sure mantra points to an existing camera."
        assert hou.node(node.parm("camera").eval()), msg.format(camera)
