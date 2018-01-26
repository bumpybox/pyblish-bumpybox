from pyblish_bumpybox import plugin


class IntegrateCollection(plugin.InstancePlugin):
    """ Convert clique collection to string.

    Negative offset to come before Deadine submission.
    """

    order = plugin.IntegratorOrder - 0.1
    label = "Collection"
    families = ["deadline"]

    def process(self, instance):

        if "collection" in instance.data:
            collection = instance.data["collection"]
            instance.data["collection"] = collection.format()
