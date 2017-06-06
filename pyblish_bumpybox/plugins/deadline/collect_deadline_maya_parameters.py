import pyblish.api


class CollectDeadlineMayaParameters(pyblish.api.ContextPlugin):
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

            # Gettng chunk size
            try:
                value = node.deadlineChunkSize.get()
                instance.data["deadlineChunkSize"] = value
            except:
                msg = "No existing \"deadlineChunkSize\" parameter."
                self.log.warning(msg)

            # Gettng priority
            try:
                value = node.deadlinePriority.get()
                instance.data["deadlinePriority"] = value
            except:
                msg = "No existing \"deadlinePriority\" parameter."
                self.log.warning(msg)

            # Gettng pool
            try:
                value = node.deadlinePool.get()
                instance.data["deadlinePool"] = value
            except:
                msg = "No existing \"deadlinePool\" parameter."
                self.log.warning(msg)

            # Gettng concurrent tasks
            try:
                value = node.deadlineConcurrentTasks.get()
                instance.data["deadlineConcurrentTasks"] = value
            except:
                msg = "No existing \"deadlineConcurrentTasks\" parameter."
                self.log.warning(msg)
