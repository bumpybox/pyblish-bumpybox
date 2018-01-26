from pyblish import api


class CollectScene(api.ContextPlugin):
    """ Converts the path flag value to the current file in the context. """

    order = api.CollectorOrder

    def process(self, context):

        context.data["currentFile"] = context.data("kwargs")["path"][0]
