import pyblish.api


class BumpyboxCollectWorkaround(pyblish.api.ContextPlugin):
    """ Temporary fix for pyblish-lite/#59 """

    order = pyblish.api.CollectorOrder - 0.4
    label = "Workaround"

    def process(self, context):

        context.create_instance("AAAAA - workaround")
