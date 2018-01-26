from pyblish import api


class ValidateMantraCamera(api.ContextPlugin):
    """ Validates that the camera for mantra nodes exists. """

    families = ["mantra"]
    order = api.ValidatorOrder
    label = "Mantra Camera"
    hosts = ["houdini"]

    def process(self, instance):
        import hou

        node = instance[0]
        camera = node.parm("camera").eval()

        msg = "Camera \"{0}\" does not exist."
        msg += "\nMake sure mantra points to an existing camera."
        assert hou.node(node.parm("camera").eval()), msg.format(camera)
