from pyblish_bumpybox import plugin


plugin.register_host('tvpaint')


class CollectSceneArg(plugin.Collector):
    """"""

    order = plugin.Collector.order - 0.05

    def process(self, context):

        path = context.data('kwargs')['data']['scene']
        context.set_data('currentFile', value=path)
