from pyblish_bumpybox import plugin


class CollectSorting(plugin.Collector):
    # offset to execute last of all collectors
    order = plugin.Collector.order + 0.49
    label = "Sorting"
    targets = ["default", "process"]

    def process(self, context):

        context[:] = sorted(
            context, key=lambda instance: (
                instance.data("family"), instance.data("label")
            )
        )
