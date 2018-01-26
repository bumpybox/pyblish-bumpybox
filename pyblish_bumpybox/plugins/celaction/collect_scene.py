from pyblish_bumpybox import plugin


class CollectScene(plugin.ContextPlugin):
    """ Converts the path flag value to the current file in the context. """

    order = plugin.CollectorOrder

    def process(self, context):

        context.data["currentFile"] = context.data("kwargs")["path"][0]
