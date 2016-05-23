import pyblish.api


class CollectCelActionScene(pyblish.api.ContextPlugin):
    """ Converts the path flag value to the current file in the context. """

    order = pyblish.api.CollectorOrder - 0.05

    def process(self, context):

        path = context.data('kwargs')['path'][0]
        context.set_data('currentFile', value=path)
