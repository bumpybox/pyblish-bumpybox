import pyblish.api
import ftrack
import pyblish_standalone


def toggle_instance(instance, new_value, old_value):

    pyblish_standalone.kwargs[str(instance)] = new_value


pyblish.api.deregister_all_callbacks()
pyblish.api.register_callback("instanceToggled", toggle_instance)


class CollectRender(pyblish.api.ContextPlugin):
    """ Adds the celaction render instance """

    order = pyblish.api.CollectorOrder + 0.1

    def process(self, context):

        # common data
        fps = 25
        task = ftrack.Task(context.data['ftrackData']['Task']['id'])
        assets = task.getParent().getAssets(assetTypes=['audio'])
        audio = None
        for a in assets:
            for v in a.getVersions():
                audio = v.getComponent().getFilesystemPath()

        # scene render
        instance = context.create_instance(name='scene')
        instance.set_data('family', value='render')

        # getting instance state
        instance.data["publish"] = False
        if pyblish_standalone.kwargs.get('scene', False):
            instance.data["publish"] = True

        data = context.data('kwargs')['data']
        for item in data:
            instance.set_data(item, value=data[item])

        instance.data["movie"] = {"fps": fps,
                                  "first_frame": int(data['start']),
                                  "audio": audio}

        instance.set_data('ftrackComponents', value={})
        instance.set_data('ftrackAssetType', value='img')

        ftrack_data = context.data('ftrackData')
        task_name = ftrack_data['Task']['name'].replace(' ', '_').lower()
        instance.set_data('ftrackAssetName', value=task_name)

        # levels render
        instance = context.create_instance(name='levels')
        instance.set_data('family', value='render')
        instance.set_data('levelSplit', value=True)

        # getting instance state
        instance.data["publish"] = False
        if pyblish_standalone.kwargs.get('levels', False):
            instance.data["publish"] = True

        data = context.data('kwargs')['data']
        for item in data:
            instance.set_data(item, value=data[item])

        instance.data["movie"] = {"fps": fps,
                                  "first_frame": int(data['start']),
                                  "audio": audio}

        instance.set_data('ftrackComponents', value={})
        instance.set_data('ftrackAssetType', value='img')

        ftrack_data = context.data('ftrackData')
        task_name = ftrack_data['Task']['name'].replace(' ', '_').lower()
        instance.set_data('ftrackAssetName', value=task_name)
