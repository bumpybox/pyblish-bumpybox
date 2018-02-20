from pyblish import api
from pyblish_bumpybox import inventory


class CollectMayaParameters(api.ContextPlugin):
    """ Add optional parameters to remote instances.

    A ContextPlugin because if remote instance is unpublishable,
    it won't activate the processing.
    Offset from default order, to pick up on created instances.
    """

    order = inventory.get_order(__file__, "CollectMayaParameters")
    label = "Maya Parameters"
    hosts = ["maya"]
    targets = ["process.deadline"]

    def process(self, context):

        for instance in context:

            # Filter to remote instances only
            if "deadline" not in instance.data.get("families", []):
                continue

            node = instance[0]

            # Gettng chunk size
            try:
                value = node.deadlineChunkSize.get()
                instance.data["deadlineChunkSize"] = value
            except AttributeError:
                msg = "No existing \"deadlineChunkSize\" parameter."
                self.log.debug(msg)

            # Gettng priority
            try:
                value = node.deadlinePriority.get()
                instance.data["deadlinePriority"] = value
            except AttributeError:
                msg = "No existing \"deadlinePriority\" parameter."
                self.log.debug(msg)

            # Gettng pool
            try:
                value = node.deadlinePool.get()
                instance.data["deadlinePool"] = value
            except AttributeError:
                msg = "No existing \"deadlinePool\" parameter."
                self.log.debug(msg)

            # Gettng concurrent tasks
            try:
                value = node.deadlineConcurrentTasks.get()
                instance.data["deadlineConcurrentTasks"] = value
            except AttributeError:
                msg = "No existing \"deadlineConcurrentTasks\" parameter."
                self.log.debug(msg)
