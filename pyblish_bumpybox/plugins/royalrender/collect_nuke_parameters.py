import pyblish.api


class BumpyboxRoyalRenderCollectNukeParameters(pyblish.api.ContextPlugin):
    """ Add optional parameters to remote instances.

    A ContextPlugin because if remote instance is unpublishable,
    it won't activate the processing.
    Offset from default order, to pick up on created instances.
    """

    order = pyblish.api.CollectorOrder + 0.2
    label = "Parameters"
    hosts = ["nuke"]

    def process(self, context):

        for instance in context:

            # Filter to remote instances only
            if "remote" not in instance.data.get("families", []):
                continue

            node = instance[0]

            # Gettng priority
            if "royalRenderPriority" in node.knobs():
                value = node["royalRenderPriority"].getValue()
                instance.data["royalRenderPriority"] = value
            else:
                msg = "No existing \"royalRenderPriority\" parameter."
                self.log.info(msg)
