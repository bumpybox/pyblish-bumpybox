import os
import subprocess

import pyblish.api
import ftrack


class IntegrateStatus(pyblish.api.Integrator):

    families = ['render']
    order = pyblish.api.Integrator.order + 0.1

    def GetStatusByName(self, name):
        statuses = ftrack.getTaskStatuses()

        result = None
        for s in statuses:
            if s.get('name').lower() == name.lower():
                result = s

        return result

    def process(self, instance, context):

        ftrack_data = context.data('ftrackData')
        task = ftrack.Task(context.data('ftrackData')['Task']['id'])

        task.setStatus(self.GetStatusByName('supervisor review'))
