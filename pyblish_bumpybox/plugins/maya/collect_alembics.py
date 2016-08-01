import pymel
import pyblish.api


class CollectAlembics(pyblish.api.Collector):
    """
    """

    def process(self, context):

        for t in pymel.core.ls(type='transform'):
            if pymel.core.general.hasAttr(t, 'pyblish_alembic'):

                instance = context.create_instance(name=str(t))
                instance.set_data('family', value='alembic.asset')
                instance.data['publish'] = t.pyblish_alembic.get()
                instance.add(t)

                # adding ftrack data to activate processing
                if not context.has_data('ftrackData'):
                    continue

                ftrack_data = context.data('ftrackData')

                instance.set_data('ftrackComponents', value={})
                instance.set_data('ftrackAssetType', value='cache')

                asset_name = ftrack_data['Task']['name']
                instance.set_data('ftrackAssetName', value=asset_name)

        for s in pymel.core.ls(type='objectSet'):
            if pymel.core.general.hasAttr(s, 'pyblish_alembic'):

                instance = context.create_instance(name=str(s))
                instance.set_data('family', value='alembic.asset')
                instance.data['publish'] = s.pyblish_alembic.get()

                # adding ftrack data to activate processing
                if not context.has_data('ftrackData'):
                    continue

                ftrack_data = context.data('ftrackData')

                instance.set_data('ftrackComponents', value={})
                instance.set_data('ftrackAssetType', value='cache')

                asset_name = ftrack_data['Task']['name']
                instance.set_data('ftrackAssetName', value=asset_name)

                for m in s.members():
                    instance.add(m)

        for c in pymel.core.ls(type='camera'):
            node = c.getParent()

            # sometimes lights can get picked up as cameras
            light_shape = False
            for shp in node.getShapes():
                if shp.nodeType() == 'directionalLight':
                    light_shape = True

            if light_shape:
                continue

            # disregard standard camera
            if node.name() in ['persp', 'front', 'side', 'top']:
                continue

            instance = context.create_instance(name=str(node))
            instance.set_data('family', value='alembic.camera')
            instance.add(node)
            instance.data["publish"] = True
            try:
                attr = getattr(node, "pyblish_camera")
                instance.data["publish"] = attr.get()
            except:
                msg = "Attribute \"{0}\"".format("pyblish_camera")
                msg += " does not exists on: \"{0}\".".format(node.name())
                msg += " Defaulting to active publish"
                self.log.info(msg)

            # adding ftrack data to activate processing
            if not context.has_data('ftrackData'):
                continue

            ftrack_data = context.data('ftrackData')

            instance.set_data('ftrackComponents', value={})
            instance.set_data('ftrackAssetType', value='cache')

            asset_name = ftrack_data['Task']['name']
            instance.set_data('ftrackAssetName', value=asset_name)
