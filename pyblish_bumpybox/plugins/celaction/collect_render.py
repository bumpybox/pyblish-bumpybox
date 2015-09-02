import pyblish.api


class CollectRender(pyblish.api.Collector):
    """"""

    order = pyblish.api.Collector.order + 0.1

    def process(self, context):

        instance = context.create_instance(name='celaction')
        instance.set_data('family', value='render')

        data = context.data('kwargs')['data']
        for item in data:
            instance.set_data(item, value=data[item])

        instance.set_data('ftrackComponents', value={})
        instance.set_data('ftrackAssetType', value='img')

        ftrack_data = context.data('ftrackData')
        task_name = ftrack_data['Task']['name'].replace(' ', '_').lower()
        instance.set_data('ftrackAssetName', value=task_name)
