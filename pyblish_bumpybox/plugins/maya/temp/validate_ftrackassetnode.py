import pymel
import pyblish.api


class ValidateFtrackAssetNode(pyblish.api.Validator):
    """
    """

    families = ['scene']
    optional = True
    label = 'FtrackAssetNode'
    exclusion = """
    renderLayer
    groupId
    reference
    displayLayer
    renderLayerManager
    script
    reference
    displayLayerManager
    script
    hyperLayout
    """

    def process(self, instance, context):

        if not context.has_data('ftrackData'):
            return

        check = True


        for node in pymel.core.ls(type='transform'):
            if not node.isReferenced():
                for f in node.listConnections(type='ftrackAssetNode'):
                    self.log.info(node)
                    check = False

                for shp in node.getShapes():
                    for f in shp.listConnections(type='ftrackAssetNode'):
                        self.log.info(shp)
                        check = False

        msg = 'None essential ftrackAssetNode connections in scene.'
        assert check, msg

        ftrack_asset_nodes = []
        for node in pymel.core.ls(type='ftrackAssetNode'):
            check = True
            for n in node.listConnections():
                if n.isReferenced():
                    check = False

            if check:
                ftrack_asset_nodes.append(node)

        msg = 'None essential ftrackAssetNode in scene:'
        msg += ' %s' % ftrack_asset_nodes
        assert len(ftrack_asset_nodes) == 0, msg

    def repair(self, instance):

        for node in pymel.core.ls(type='transform'):
            if not node.isReferenced():
                for f in node.listConnections(type='ftrackAssetNode'):
                    f.assetLink // node.ftrack

                for shp in node.getShapes():
                    for f in shp.listConnections(type='ftrackAssetNode'):
                        f.assetLink // shp.ftrack

        ftrack_asset_nodes = []
        for node in pymel.core.ls(type='ftrackAssetNode'):
            check = True
            for n in node.listConnections():
                if n.isReferenced():
                    check = False

            if check:
                pymel.core.delete(node)
