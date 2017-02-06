import pymel.core as pm
import pyblish.api


class BumpyboxMayaRepairArnoldSettings(pyblish.api.Action):

    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):

        node = pm.PyNode("defaultArnoldDriver")
        node.mergeAOVs.set(True)


class BumpyboxMayaValidateArnoldSettings(pyblish.api.InstancePlugin):
    """ Validates render layer settings. """

    order = pyblish.api.ValidatorOrder
    optional = True
    families = ["renderlayer"]
    label = "Arnold Settings"
    actions = [BumpyboxMayaRepairArnoldSettings]
    hosts = ["maya"]

    def process(self, instance):

        node = pm.PyNode("defaultArnoldDriver")
        assert node.mergeAOVs.get(), "AOVs needs to be merged."
