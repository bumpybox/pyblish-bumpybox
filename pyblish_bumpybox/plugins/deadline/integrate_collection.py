from pyblish import api


class IntegrateCollection(api.ContextPlugin):
    """ Convert clique collection to string.

    Negative offset to come before Deadine submission.
    """

    order = api.IntegratorOrder - 0.1
    label = "Collection"
    families = ["deadline"]

    def process(self, instance):

        if "collection" in instance.data:
            collection = instance.data["collection"]
            instance.data["collection"] = collection.format()
