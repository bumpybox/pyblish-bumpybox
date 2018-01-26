from pyblish import api


class CollectSorting(api.ContextPlugin):
    # offset to execute last of all collectors
    order = api.CollectorOrder + 0.49
    label = "Sorting"
    targets = ["default", "process"]

    def process(self, context):

        context[:] = sorted(
            context, key=lambda instance: (
                instance.data("family"), instance.data("label")
            )
        )
