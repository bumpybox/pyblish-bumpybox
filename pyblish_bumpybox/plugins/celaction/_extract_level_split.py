import pyblish.api


class ExtractDeadline(pyblish.api.InstancePlugin):
    """ Optional plugin to split the render into levels. """

    label = 'Split Levels'
    publish = False
    families = ['render']
    optional = True
    order = pyblish.api.ExtractorOrder - 0.2

    def process(self, instance):

        instance.set_data('levelSplit', value=True)
