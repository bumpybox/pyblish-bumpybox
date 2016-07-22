import hou
import pyblish.api


class ValidateMantraCamera(pyblish.api.InstancePlugin):
    """ Validates mantra settings """

    families = ["img.*", "render.*"]
    order = pyblish.api.ValidatorOrder
    label = "Mantra Camera"

    def process(self, instance):

        node = instance[0]
        camera = node.parm("camera").eval()

        msg = "Camera \"{0}\" does not exist.".format(camera)
        msg += "\nMake sure mantra points to an existing camera."
        assert hou.node(node.parm("camera").eval()), msg
