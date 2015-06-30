import pyblish.api


@pyblish.api.log
class SelectMayaRemoveDefaulrenderlayer(pyblish.api.Selector):
    """ Removes default renderlayer from context"""

    order = pyblish.api.Selector.order + 0.1
    hosts = ['maya']

    def process(self, context):

        for instance in context:
            if str(instance) == 'defaultRenderLayer':
                context.remove(instance)
