from pyblish import api


class RepairAssetsAction(api.Action):

    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):
        import pymel.core as pc

        for node in pc.ls(type="ftrackAssetNode"):
            if not node.assetLink.connections():
                pc.delete(node)


class ValidateAssets(api.ContextPlugin):
    """ Validates clean up broken Ftrack assets. """

    order = api.ValidatorOrder
    families = ["scene"]
    optional = True
    label = "Assets"
    actions = [RepairAssetsAction]
    hosts = ["maya"]

    def process(self, context):
        import pymel.core as pc

        for node in pc.ls(type="ftrackAssetNode"):
            msg = "Ftrack Asset link on \"{0}\" is broken.".format(node.name())
            assert node.assetLink.connections(), msg
