import os

import pyblish.api
import ftrack


@pyblish.api.log
class SelectFtrackAssetName(pyblish.api.Selector):
    """ """

    hosts = ['*']
    version = (0, 1, 0)

    def process_context(self, context):

        task = ftrack.Task(id=os.environ['FTRACK_TASKID'])
        context.set_data('ftrackAssetName', value=task.getName())
