import pyblish.api


class BumpyboxDeadlineCollectFamily(pyblish.api.InstancePlugin):
    """ Append Deadline data to "farm" instances. """

    order = pyblish.api.CollectorOrder + 0.4
    families = ["farm"]
    label = "Family"

    def process(self, instance):

        instance.data["families"] += ["deadline"]
