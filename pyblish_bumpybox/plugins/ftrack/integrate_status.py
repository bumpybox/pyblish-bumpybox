from pyblish_bumpybox import plugin


class IntegrateStatus(plugin.ContextPlugin):
    """ Sets the task to "In Progress". """

    order = plugin.IntegratorOrder
    label = "Ftrack Status"
    optional = True

    def process(self, context):

        session = context.data["ftrackSession"]
        status = session.query("Status where name is \"In Progress\"").one()
        context.data["ftrackTask"]["status"] = status
        session.commit()
