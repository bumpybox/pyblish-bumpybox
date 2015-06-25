import os

import pyblish.api


@pyblish.api.log
class SelectFtrackAssetName(pyblish.api.Selector):
    """ """

    order = pyblish.api.Selector.order + 0.2
    hosts = ['*']
    version = (0, 1, 0)

    def process(self, context):

        # skipping if not launched from ftrack
        if not context.has_data('ftrackData'):
            return

        # on going project specific exception
        ftrack_data = context.data('ftrackData')
        if ftrack_data['Project']['code'] == 'the_call_up':
            return

        # setting ftrackAssetName
        task_name = ftrack_data['Task']['name']
        self.log.info('Setting ftrackAssetName: %s' % task_name)
        context.set_data('ftrackAssetName', value=task_name)
