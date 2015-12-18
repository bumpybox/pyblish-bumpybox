import pymel
import pyblish.api


class CollectAlembics(pyblish.api.Collector):
    """
    """

    def process(self, context):

        asset_nodes = []
        for t in pymel.core.ls(type='transform'):
            if pymel.core.general.hasAttr(t, 'pyblish_alembic') and \
            t.pyblish_alembic.get():

                instance = context.create_instance(name=str(t))
                instance.set_data('family', value='alembic.asset')
                instance.add(t)

                asset_nodes.append(t)

                # adding ftrack data to activate processing
                if not context.has_data('ftrackData'):
                    continue

                ftrack_data = context.data('ftrackData')

                instance.set_data('ftrackComponents', value={})
                instance.set_data('ftrackAssetType', value='cache')

                asset_name = ftrack_data['Task']['name']
                instance.set_data('ftrackAssetName', value=asset_name)
        """
        roots = {}
        for node in pymel.core.ls(type='transform'):
            if pymel.core.general.hasAttr(node, 'pyblish_alembic'):
                if node.root() in roots:
                    roots[node.root()].append(node)
                else:
                    roots[node.root()] = [node]

        for r in roots:
            data = []
            for node in roots[r]:
                temp = node.getAllParents()
                if len(temp) > len(data):
                    data = temp

            for node in roots[r]:
                for p in data:
                    if p not in node.getAllParents():
                        data.remove(p)

            instance = context.create_instance(name=str(data[0]))
            instance.set_data('family', value='alembic.asset')
            instance.add(data[0])

            # adding ftrack data to activate processing
            if not context.has_data('ftrackData'):
                continue

            ftrack_data = context.data('ftrackData')

            instance.set_data('ftrackComponents', value={})
            instance.set_data('ftrackAssetType', value='cache')

            asset_name = ftrack_data['Task']['name']
            instance.set_data('ftrackAssetName', value=asset_name)

        for s in pymel.core.ls(type='mesh'):
            node = s.getParent()

            if node in asset_nodes:
                continue

            instance = context.create_instance(name=str(node))
            instance.set_data('family', value='alembic')
            instance.add(node)

            # adding ftrack data to activate processing
            if not context.has_data('ftrackData'):
                continue

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
            if not context.has_data('ftrackData'):
                continue

            ftrack_data = context.data('ftrackData')

            instance.set_data('ftrackComponents', value={})
            instance.set_data('ftrackAssetType', value='cache')

            asset_name = ftrack_data['Task']['name']
            instance.set_data('ftrackAssetName', value=asset_name)
