import pyblish.api


class BumpyboxDeadlineCollectOptionalParameters(pyblish.api.ContextPlugin):
    """ Add optional parameters to remote instances.

    A ContextPlugin because if remote instance is unpublishable,
    it won't activate the processing.
    Offset from default order, to pick up on created houdini instances.
    """

    order = pyblish.api.CollectorOrder + 0.1
    label = "Optional Parameters"
    hosts = ["houdini"]

    def process(self, context):

        for instance in context:

            # Filter to remote instances only
            if "remote" not in instance.data.get("families", []):
                continue

            node = instance[0]

            # Gettng chunk size
            try:
                value = node.parm("deadlineChunkSize").eval()
                instance.data["deadlineChunkSize"] = value
            except:
                msg = "No existing \"deadlineChunkSize\" parameter."
                self.log.info(msg)

            # Gettng priority
            try:
                value = node.parm("deadlinePriority").eval()
                instance.data["deadlinePriority"] = value
            except:
                msg = "No existing \"deadlinePriority\" parameter."
                self.log.info(msg)

            # Gettng priority
            try:
                value = node.parm("deadlinePool").eval()
                instance.data["deadlinePool"] = value
            except:
                msg = "No existing \"deadlinePool\" parameter."
                self.log.info(msg)

            # Gettng priority
            try:
                value = node.parm("deadlinePool").eval()
                instance.data["deadlinePool"] = value
            except:
                msg = "No existing \"deadlinePool\" parameter."
                self.log.info(msg)

            # Gettng concurrent tasks
            try:
                value = node.parm("deadlineConcurrentTasks").eval()
                instance.data["deadlineConcurrentTasks"] = value
            except:
                msg = "No existing \"deadlineConcurrentTasks\" parameter."
                self.log.info(msg)
