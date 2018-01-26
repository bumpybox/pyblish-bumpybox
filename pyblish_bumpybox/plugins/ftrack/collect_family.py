from pyblish import api


class CollectFamily(api.ContextPlugin):
    """ Adds the "ftrack" family to all instanes. """

    # Offset to get all instances
    order = api.CollectorOrder + 0.4
    label = "Ftrack Family"

    def process(self, context):

        for instance in context:

            # Add ftrack family
            families = instance.data.get("families", [])
            instance.data["families"] = families + ["ftrack"]
