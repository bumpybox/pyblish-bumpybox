import pyblish.api


class CollectDeadlineNukeParameters(pyblish.api.ContextPlugin):
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

            # Gettng chunk size
            if "deadlineChunkSize" in node.knobs():
                value = node["deadlineChunkSize"].getValue()
                instance.data["deadlineChunkSize"] = value
            else:
                msg = "No existing \"deadlineChunkSize\" parameter."
                self.log.info(msg)

            # Gettng priority
            if "deadlinePriority" in node.knobs():
                value = node["deadlinePriority"].getValue()
                instance.data["deadlinePriority"] = value
            else:
                msg = "No existing \"deadlinePriority\" parameter."
                self.log.info(msg)

            # Gettng pool
            if "deadlinePool" in node.knobs():
                value = node["deadlinePool"].getValue()
                instance.data["deadlinePool"] = value
            else:
                msg = "No existing \"deadlinePool\" parameter."
                self.log.info(msg)

            # Gettng limits
            if "deadlineLimits" in node.knobs():
                value = node["deadlineLimits"].getValue()
                instance.data["deadlineLimits"] = value
            else:
                msg = "No existing \"deadlineLimits\" parameter."
                self.log.info(msg)

            # Gettng concurrent tasks
            if "deadlineConcurrentTasks" in node.knobs():
                value = node["deadlineConcurrentTasks"].getValue()
                instance.data["deadlineConcurrentTasks"] = value
            else:
                msg = "No existing \"deadlineConcurrentTasks\" parameter."
                self.log.info(msg)
