import pymel.core as pc

import pyblish.api


class RepairFtrackAssetsAction(pyblish.api.Action):

    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):

        for node in pc.ls(type="ftrackAssetNode"):
            if not node.assetLink.connections():
                pc.delete(node)


class ValidateFtrackAssets(pyblish.api.Validator):
    """ Validates clean up broken Ftrack assets. """

    families = ["scene"]
    optional = True
    label = "Assets"
    actions = [RepairFtrackAssetsAction]
    hosts = ["maya"]

    def process(self, context):

        for node in pc.ls(type="ftrackAssetNode"):
            msg = "Ftrack Asset link on \"{0}\" is broken.".format(node.name())
            assert node.assetLink.connections(), msg
