import pyblish.api


class ValidateTask(pyblish.api.Validator):

    families = ['task']
    label = 'Task'
    optional = True

    def process(self, instance):

        self.log.info(instance.data['taskName'])
        assert False, 'stop'
