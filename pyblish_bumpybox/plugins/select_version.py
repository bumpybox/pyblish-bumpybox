import os

import pyblish.api
import pyseq

import ftrack


@pyblish.api.log
class SelectVersion(pyblish.api.Selector):
    """"""

    order = pyblish.api.Selector.order + 0.2
    hosts = ['ftrack']

    def process(self, context):

        ftrack_data = context.data('ftrackData')

        task = ftrack.Task(ftrack_data['Task']['id'])

        parent = task.getParent()

        assets = parent.getAssets(assetTypes=['img'])
        version_number = 1
        if assets:
            for a in assets:
                if a.getName() == ftrack_data['Task']['name']:
                    version_number = a.getVersions()[-1].getVersion() + 1

        self.log.info(version_number)

        context.set_data('version', value=version_number)
