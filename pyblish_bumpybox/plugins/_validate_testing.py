import pyblish.api


class ValidateTesting(pyblish.api.Validator):
    """"""

    families = ['deadline.render']

    def process(self, instance):

        self.log.info(instance.data['publish'])

        assert False
