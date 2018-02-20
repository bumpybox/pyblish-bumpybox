from pyblish import api
from pyblish_bumpybox import inventory


class CollectFamily(api.ContextPlugin):
    """Append "deadline" family to instances."""

    order = inventory.get_order(__file__, "CollectFamily")
    label = "Family"
    targets = ["process.deadline"]

    def process(self, context):

        for instance in context:
            families = [instance.data["family"]] + instance.data["families"]
            if "source" in families:
                continue

            instance.data["families"] += ["deadline"]
