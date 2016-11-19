import pyblish.api


class BumpyboxDeadlineIntegrateCollection(pyblish.api.InstancePlugin):
    """ Convert clique collection to string. """

    order = pyblish.api.IntegratorOrder
    label = "Collection"

    def process(self, instance):

        if "collection" in instance.data:
            collection = instance.data["collection"]
            instance.data["collection"] = collection.format()
