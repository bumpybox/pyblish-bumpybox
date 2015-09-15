import pymel
import pyblish.api


class CollectAlembics(pyblish.api.Collector):
    """
    """

    def process(self, context):

        asset_nodes = []
        for t in pymel.core.ls(type='transform'):
            if pymel.core.general.hasAttr(t, 'pyblish_alembic'):

                instance = context.create_instance(name=str(t))
                instance.set_data('family', value='alembic.asset')
                instance.add(t)

                asset_nodes.append(t)

                # adding ftrack data to activate processing
                ftrack_data = context.data('ftrackData')

                instance.set_data('ftrackComponents', value={})
                instance.set_data('ftrackAssetType', value='cache')

                asset_name = ftrack_data['Task']['name']
                instance.set_data('ftrackAssetName', value=asset_name)
        """
        for s in pymel.core.ls(type='mesh'):
            node = s.getParent()

            if node in asset_nodes:
                continue

            instance = context.create_instance(name=str(node))
            instance.set_data('family', value='alembic')
            instance.add(node)

            # adding ftrack data to activate processing
            ftrack_data = context.data('ftrackData')

            instance.set_data('ftrackComponents', value={})
            instance.set_data('ftrackAssetType', value='cache')

            asset_name = ftrack_data['Task']['name']
            instance.set_data('ftrackAssetName', value=asset_name)
        """

        for c in pymel.core.ls(type='camera'):
            node = c.getParent()

            if node.name() in ['persp', 'front', 'side', 'top']:
                continue

            instance = context.create_instance(name=str(node))
            instance.set_data('family', value='alembic.camera')
            instance.add(node)

            # adding ftrack data to activate processing
            ftrack_data = context.data('ftrackData')

            instance.set_data('ftrackComponents', value={})
            instance.set_data('ftrackAssetType', value='cache')

            asset_name = ftrack_data['Task']['name']
            instance.set_data('ftrackAssetName', value=asset_name)
