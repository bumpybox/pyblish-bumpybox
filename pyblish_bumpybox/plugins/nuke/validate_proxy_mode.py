from pyblish_bumpybox import plugin


class RepairProxyModeAction(plugin.Action):

    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):
        import nuke
        nuke.root()["proxy"].setValue(0)


class ValidateProxyMode(plugin.ContextPlugin):
    """Validates against having proxy mode on."""

    order = plugin.ValidatorOrder
    optional = True
    label = "Proxy Mode"
    actions = [RepairProxyModeAction]
    hosts = ["nuke", "nukeassist"]
    targets = ["default", "process"]

    def process(self, context):
        import nuke
        msg = (
            "Proxy mode is not supported. Please disable Proxy Mode in the "
            "Project settings."
        )
        assert not nuke.root()["proxy"].getValue(), msg
