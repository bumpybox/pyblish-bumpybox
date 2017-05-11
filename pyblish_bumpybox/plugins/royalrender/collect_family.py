import pyblish.api


class BumpyboxRoyalRenderCollectFamily(pyblish.api.ContextPlugin):
    """ Append "royalrender" to instances of "remote" family """

    order = pyblish.api.CollectorOrder + 0.4
    label = "Family"

    def process(self, context):

        for instance in context:
            if "remote" in instance.data.get("families", []):
                instance.data["families"] += ["royalrender"]
