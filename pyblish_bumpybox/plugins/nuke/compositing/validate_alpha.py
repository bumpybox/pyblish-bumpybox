import nuke
import pyblish.api


class ValidateAlpha(pyblish.api.Validator):
    """ HoBsoft specific request for no alpha
    """

    families = ['deadline.render']
    optional = True
    label = 'Alpha'

    def process(self, instance):

        node = instance[0]

        msg = '%s is not writing out the correct channels.' % node.name()
        msg += ' Should be "rgb"'
        assert node['channels'].value() == 'rgb', msg

    def repair(self, instance):

        node = instance[0]

        node['channels'].setValue('rgb')
