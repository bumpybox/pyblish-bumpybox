import pyblish.api
import ftrack


@pyblish.api.log
class ValidateFtrackStatus(pyblish.api.Validator):
    """ Extract work file to 'publish' directory next to work file
    """

    families = ['scene']
    label = 'Update FTrack Status'

    def GetStatusByName(self, name):
        statuses = ftrack.getTaskStatuses()

        result = None
        for s in statuses:
            if s.get('name').lower() == name.lower():
                result = s

        return result

    def process(self, context, instance):

        task = ftrack.Task(context.data('ftrackData')['Task']['id'])

        if task.getStatus().getName().lower() != 'in progress':
            task.setStatus(self.GetStatusByName('in progress'))
