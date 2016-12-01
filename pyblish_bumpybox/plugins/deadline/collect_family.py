import pyblish.api


class BumpyboxDeadlineCollectFamily(pyblish.api.ContextPlugin):
    """ Append Deadline data to "farm" instances. """

    order = pyblish.api.CollectorOrder + 0.4
    label = "Family"

    def process(self, context):

        for instance in context:
            if "farm" in instance.data.get("families", []):
                instance.data["families"] += ["deadline"]
