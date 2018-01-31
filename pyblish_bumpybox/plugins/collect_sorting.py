from pyblish import api
from pyblish_bumpybox import inventory


class CollectSorting(api.ContextPlugin):
    # offset to execute last of all collectors
    order = inventory.get_order(__file__, "CollectSorting")
    label = "Sorting"
    targets = ["default", "process"]

    def process(self, context):

        context[:] = sorted(
            context, key=lambda instance: (
                instance.data("family"), instance.data("label")
            )
        )
