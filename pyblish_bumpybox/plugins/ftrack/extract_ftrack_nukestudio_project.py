import pyblish.api


class ExtractFtrackProject(pyblish.api.ContextPlugin):
    """Extract an Ftrack project from context.data["ftrackProjectData"]"""

    order = pyblish.api.ExtractorOrder
    label = "Ftrack Project"
    hosts = ["nukestudio"]

    def process(self, context):

        session = context.data["ftrackSession"]

        data = {}
        for key, value in context.data["ftrackProjectData"].iteritems():
            if not value:
                continue

            data[key] = value

        # Get project from data
        query = "Project where "
        for key, value in data.iteritems():
            query += "{0} is \"{1}\" and ".format(key, value)
        query = query[:-5]

        project = session.query(query).first()

        # Create project if it does not exist
        if not project:
            self.log.info("Creating project with data: {0}".format(data))
            project = session.create("Project", data)
            session.commit()

        context.data["ftrackProject"] = project
