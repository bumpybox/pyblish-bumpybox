import pyblish.api
import ftrack


class ValidateFtrackStatus(pyblish.api.Validator):

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


class DeadlineFtrackStatus(pyblish.api.Integrator):

    order = pyblish.api.Integrator.order - 0.1

    def process(self, context):

        instances = {}
        instances_order = []
        instances_no_order = []

        for instance in context:

            if not instance.data.get("publish", True):
                continue

            # skipping instance if data is missing
            if not instance.has_data('deadlineData'):
                msg = 'No deadlineData present. Skipping "%s"' % instance
                self.log.info(msg)
                continue

            if 'order' in instance.data('deadlineData'):
                order = instance.data('deadlineData')['order']
                instances_order.append(order)
                if order in instances:
                    instances[order].append(instance)
                else:
                    instances[order] = [instance]
            else:
                instances_no_order.append(instance)

        instances_order = list(set(instances_order))
        instances_order.sort()

        new_context = []
        for order in instances_order:
            for instance in instances[order]:
                new_context.append(instance)

        if not instances_order:
            new_context = instances_no_order

        if not new_context:
            return

        for instance in new_context[:-1]:
            data = instance.data['deadlineData']['job']
            if 'ExtraInfoKeyValue' in data:
                data['ExtraInfoKeyValue']['FT_StatusUpdate'] = False

        data = new_context[-1].data['deadlineData']['job']
        if 'ExtraInfoKeyValue' in data:
            data['ExtraInfoKeyValue']['FT_StatusUpdate'] = True
