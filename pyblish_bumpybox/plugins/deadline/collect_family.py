from pyblish import api
from pyblish_bumpybox import inventory


class CollectFamily(api.ContextPlugin):
    """ Append Deadline data to "remote" instances. """

    order = inventory.get_order(__file__, "CollectFamily")
    label = "Family"

    def process(self, context):

        for instance in context:
            if "remote" in instance.data.get("families", []):
                instance.data["families"] += ["deadline"]
