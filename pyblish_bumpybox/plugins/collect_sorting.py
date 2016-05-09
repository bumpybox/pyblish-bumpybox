import pyblish.api


class CollectSorting(pyblish.api.Collector):
    # offset to execute last of all collectors
    order = pyblish.api.Collector.order + 0.4

    def process(self, context):

        context[:] = sorted(context,
                            key=lambda instance: (instance.data("family"),
                                                  instance.data("name")))
