import os
import shutil

import pyblish.api


@pyblish.api.log
class SelectWorkfile(pyblish.api.Selector):
    """"""

    order = pyblish.api.Selector.order + 0.1
    hosts = ['*']
    version = (0, 1, 0)

    def process_context(self, context):

        current_file = context.data('currentFile')
        current_dir = os.path.dirname(current_file)
        publish_dir = os.path.join(current_dir, 'publish')
        publish_file = os.path.join(publish_dir, os.path.basename(current_file))

        # create instance
        instance = context.create_instance(name=os.path.basename(current_file))

        instance.set_data('family', value='workFile')
        instance.set_data('workPath', value=current_file)
        instance.set_data('publishPath', value=publish_file)

        # deadline data
        instance.context.set_data('deadlineInput', value=publish_file)

        # ftrack data
        components = {'publish_file': {'path': publish_file}}

        if pyblish.api.current_host() == 'nuke':
            components['nukescript'] = {'path': current_file}
        else:
            components['work_file'] = {'path': current_file}

        instance.set_data('ftrackComponents', value=components)
