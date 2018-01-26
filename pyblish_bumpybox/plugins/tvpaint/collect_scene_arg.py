from pyblish import api


api.register_host('tvpaint')


class CollectSceneArg(api.ContextPlugin):
    """"""

    order = api.CollectorOrder - 0.05

    def process(self, context):

        path = context.data('kwargs')['data']['scene']
        context.set_data('currentFile', value=path)
