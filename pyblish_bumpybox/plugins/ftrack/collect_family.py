from pyblish import api
from pyblish_bumpybox import inventory


class CollectFamily(api.ContextPlugin):
    """ Adds the "ftrack" family to all instanes. """

    # Offset to get all instances
    order = inventory.get_order(__file__, "CollectFamily")
    label = "Ftrack Family"
    targets = ["default", "process"]

    def process(self, context):

        for instance in context:

            # Add ftrack family
            families = instance.data.get("families", [])
            instance.data["families"] = families + ["ftrack"]
