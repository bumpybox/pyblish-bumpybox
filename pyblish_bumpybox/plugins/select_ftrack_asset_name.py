import os

import pyblish.api
import ftrack


@pyblish.api.log
class SelectFtrackAssetName(pyblish.api.Selector):
    """ """

    hosts = ['*']
    version = (0, 1, 0)

    def process(self, context):

        task = ftrack.Task(id=os.environ['FTRACK_TASKID'])

        # skipping the call up project
        project = task.getParents()[-1]
        if project.getName() == 'the_call_up':
            return

        # setting ftrackAssetName
        self.log.info('setting ftrackAssetName')
        context.set_data('ftrackAssetName', value=task.getName())
