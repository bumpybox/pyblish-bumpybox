import pyblish.api


class CollectSorting(pyblish.api.Collector):
    # offset to execute last of all collectors
    order = pyblish.api.Collector.order + 0.49
    label = "Sorting"
    targets = ["default", "processing"]

    def process(self, context):

        context[:] = sorted(
            context, key=lambda instance: (
                instance.data("family"), instance.data("name")
            )
        )
