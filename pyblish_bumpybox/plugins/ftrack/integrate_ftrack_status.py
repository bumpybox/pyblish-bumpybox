import pyblish.api


class IntegrateFtrackStatus(pyblish.api.ContextPlugin):
    """ Sets the task to "In Progress". """

    order = pyblish.api.IntegratorOrder
    label = "Ftrack Status"
    optional = True

    def process(self, context):

        session = context.data["ftrackSession"]
        status = session.query("Status where name is \"In Progress\"").one()
        context.data["ftrackTask"]["status"] = status
        session.commit()
