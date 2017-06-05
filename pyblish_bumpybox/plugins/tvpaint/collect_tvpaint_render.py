import pyblish.api


class CollectTVPaintRender(pyblish.api.Collector):
    """"""

    order = pyblish.api.Collector.order + 0.1

    def process(self, context):

        data = context.data('kwargs')['data']
        layers = []
        for item in data:
            if item.startswith('layer'):
                layers.append(data[item])

        for layer in layers:
            instance = context.create_instance(name=layer)
            instance.set_data('family', value='render')
            instance.data["families"] = ["deadline"]

            instance.set_data('ftrackComponents', value={})
            instance.set_data('ftrackAssetType', value='img')

            ftrack_data = context.data('ftrackData')
            task_name = ftrack_data['Task']['name'].replace(' ', '_').lower()
            instance.set_data('ftrackAssetName', value=task_name)
