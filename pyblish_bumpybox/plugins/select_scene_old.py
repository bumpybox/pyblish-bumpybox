import os

import pyblish.api


@pyblish.api.log
class SelectSceneOld(pyblish.api.Selector):
    """"""

    order = pyblish.api.Selector.order + 0.2
    hosts = ['nuke']
    version = (0, 1, 0)

    def process(self, context):

        # skipping if not launched from ftrack
        if not context.has_data('ftrackData'):
            return

        ftrack_data = context.data('ftrackData')

        current_file = context.data('currentFile')
        current_dir = os.path.dirname(current_file)
        publish_dir = os.path.join(current_dir, 'publish')
        publish_file = os.path.join(publish_dir, os.path.basename(current_file))

        # create instance
        name = os.path.basename(current_file) + '_old'
        instance = context.create_instance(name=name)

        instance.set_data('family', value='scene.old')
        instance.set_data('workPath', value=current_file)
        instance.set_data('publishPath', value=publish_file)

        # deadline data
        instance.context.set_data('deadlineInput', value=publish_file)

        # ftrack data
        components = {'publish_file': {'path': publish_file}}
        components['nukescript'] = {'path': current_file}

        # transition code
        if ftrack_data['Project']['code'] != 'the_call_up':
            task_name = ftrack_data['Task']['name']
            instance.set_data('ftrackAssetName', value=task_name)

        instance.set_data('ftrackComponents', value=components)
        instance.set_data('ftrackAssetType', value='compositing')
