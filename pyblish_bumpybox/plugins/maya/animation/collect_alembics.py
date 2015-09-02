import pymel
import pyblish.api


class CollectAlembics(pyblish.api.Collector):
    """
    """

    def process(self, context):

        alembic_nodes = []

        for t in pymel.core.ls(type='transform'):
            if pymel.core.general.hasAttr(t, 'pyblish_alembic'):
                alembic_nodes.append(t)

        for node in alembic_nodes:

            instance = context.create_instance(name=str(node))
            instance.set_data('family', value='alembic')
            instance.add(node)

            # adding ftrack data to activate processing
            ftrack_data = context.data('ftrackData')

            instance.set_data('ftrackComponents', value={})
            instance.set_data('ftrackAssetType', value='cache')

            asset_name = ftrack_data['Task']['name']
            instance.set_data('ftrackAssetName', value=asset_name)
