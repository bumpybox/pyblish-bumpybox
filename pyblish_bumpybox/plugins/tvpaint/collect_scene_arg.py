from pyblish import api
from pyblish_bumpybox import inventory


api.register_host('tvpaint')


class CollectSceneArg(api.ContextPlugin):
    """"""

    order = inventory.get_order(__file__, "CollectSceneArg")

    def process(self, context):

        path = context.data('kwargs')['data']['scene']
        context.set_data('currentFile', value=path)
