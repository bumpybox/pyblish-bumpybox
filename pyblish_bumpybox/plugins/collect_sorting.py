import pyblish.api


class BumpyboxCollectSorting(pyblish.api.Collector):
    # offset to execute last of all collectors
    order = pyblish.api.Collector.order + 0.4
    label = "Sorting"

    def process(self, context):

        context[:] = sorted(context,
                            key=lambda instance: (instance.data("name"),
                                                  instance.data("label")))
