from pyblish_bumpybox import plugin


class CollectFamily(plugin.ContextPlugin):
    """ Append Deadline data to "remote" instances. """

    order = plugin.CollectorOrder + 0.4
    label = "Family"

    def process(self, context):

        for instance in context:
            if "remote" in instance.data.get("families", []):
                instance.data["families"] += ["deadline"]
