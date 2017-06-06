import pymel.core as pm
import pyblish.api


class RepairMayaArnoldSettings(pyblish.api.Action):

    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):

        node = pm.PyNode("defaultArnoldDriver")
        node.mergeAOVs.set(True)


class ValidateMayaArnoldSettings(pyblish.api.InstancePlugin):
    """ Validates render layer settings. """

    order = pyblish.api.ValidatorOrder
    optional = True
    families = ["arnold"]
    label = "Arnold Settings"
    actions = [RepairMayaArnoldSettings]
    hosts = ["maya"]

    def process(self, instance):

        node = pm.PyNode("defaultArnoldDriver")
        assert node.mergeAOVs.get(), "AOVs needs to be merged."
