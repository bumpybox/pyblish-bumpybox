import pyblish.api


class ExtractFtrackCommit(pyblish.api.ContextPlugin):
    """Commits the Ftrack session before integration.

    Offset to be last in the extraction phase.
    """

    order = pyblish.api.ExtractorOrder + 0.4
    label = "Ftrack Commit"
    hosts = ["nukestudio"]

    def process(self, context):

        context.data["ftrackSession"].commit()
