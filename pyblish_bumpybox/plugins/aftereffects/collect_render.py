import pyblish.api


class CollectRender(pyblish.api.Collector):
    """
    """

    order = pyblish.api.Collector.order + 0.1

    def process(self, context):

        data = context.data('environmentArgs')

        check = True

        for item in data:
            if item == 'render':
                for v in data[item]:

                    try:
                        instance = context.create_instance(name=v[0])
                        instance.set_data('family', value='render')
                        instance.set_data('path', value=v[1])
                        instance.set_data('start', value=v[2])
                        instance.set_data('end', value=v[3])

                        instance.set_data('ftrackComponents', value={})
                        instance.set_data('ftrackAssetType', value='img')

                        ftrack_data = context.data('ftrackData')
                        task_name = ftrack_data['Task']['name'].replace(' ', '_')
                        task_name = task_name.lower()
                        instance.set_data('ftrackAssetName', value=task_name)
                    except:
                        check = False

        context.set_data('sameNamedRenders', value=check)
