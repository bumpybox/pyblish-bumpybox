import pyblish.api


class CollectRender(pyblish.api.ContextPlugin):
    """ Adds the celaction render instances """

    order = pyblish.api.CollectorOrder

    def process(self, context):

        # scene image render
        instance = context.create_instance(name="scene")
        instance.data["family"] = "img.local.png"
        instance.data["families"] = ["img.*", "img.local.*"]

        # getting instance state
        instance.data["publish"] = False

        # levels image render
        instance = context.create_instance(name="levels")
        instance.data["family"] = "img.local.png"
        instance.data["families"] = ["img.*", "img.local.*"]

        # getting instance state
        instance.data["publish"] = False

        # scene movie render
        instance = context.create_instance(name="scene")
        instance.data["family"] = "mov.local.mov"
        instance.data["families"] = ["mov.*", "mov.local.*"]

        # getting instance state
        instance.data["publish"] = False
