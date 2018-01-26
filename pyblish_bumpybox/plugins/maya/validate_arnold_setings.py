from pyblish_bumpybox import plugin


class RepairArnoldSettings(plugin.Action):

    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):
        import pymel.core as pm
        node = pm.PyNode("defaultArnoldDriver")
        node.mergeAOVs.set(True)


class ValidateArnoldSettings(plugin.InstancePlugin):
    """ Validates render layer settings. """

    order = plugin.ValidatorOrder
    optional = True
    families = ["arnold"]
    label = "Arnold Settings"
    actions = [RepairArnoldSettings]
    hosts = ["maya"]

    def process(self, instance):
        import pymel.core as pm
        node = pm.PyNode("defaultArnoldDriver")
        assert node.mergeAOVs.get(), "AOVs needs to be merged."
