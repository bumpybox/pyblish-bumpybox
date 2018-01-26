from pyblish import api
from pyblish_bumpybox import inventory


class CollectScene(api.ContextPlugin):
    """ Converts the path flag value to the current file in the context. """

    order = inventory.get_order(__file__, "CollectScene")

    def process(self, context):

        context.data["currentFile"] = context.data("kwargs")["path"][0]
