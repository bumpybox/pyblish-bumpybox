from pyblish import api
from pyblish_bumpybox import inventory


class IntegrateCollection(api.ContextPlugin):
    """ Convert clique collection to string.

    Negative offset to come before Deadine submission.
    """

    order = inventory.get_order(__file__, "IntegrateCollection")
    label = "Collection"
    families = ["deadline"]

    def process(self, instance):

        if "collection" in instance.data:
            collection = instance.data["collection"]
            instance.data["collection"] = collection.format()
