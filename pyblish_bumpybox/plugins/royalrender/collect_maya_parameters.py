import pyblish.api


class BumpyboxRoyalRenderCollectMayaParameters(pyblish.api.ContextPlugin):
    """ Add optional parameters to remote instances.

    A ContextPlugin because if remote instance is unpublishable,
    it won't activate the processing.
    Offset from default order, to pick up on created instances.
    """

    order = pyblish.api.CollectorOrder + 0.1
    label = "Maya Parameters"
    hosts = ["maya"]

    def process(self, context):

        for instance in context:

            # Filter to remote instances only
            if "remote" not in instance.data.get("families", []):
                continue

            node = instance[0]

            # Gettng priority
            try:
                value = node.royalRenderPriority.get()
                instance.data["royalRenderPriority"] = value
            except:
                msg = "No existing \"royalRenderPriority\" parameter."
                self.log.warning(msg)
