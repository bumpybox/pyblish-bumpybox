from pyblish import api


class IntegrateStatus(api.ContextPlugin):
    """ Sets the task to "In Progress". """

    order = api.IntegratorOrder
    label = "Ftrack Status"
    optional = True

    def process(self, context):

        session = context.data["ftrackSession"]
        status = session.query("Status where name is \"In Progress\"").one()
        context.data["ftrackTask"]["status"] = status
        session.commit()
