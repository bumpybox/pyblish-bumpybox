import pyblish.api
import ftrack


class BumpyboxFtrackValidateStatus(pyblish.api.Validator):

    families = ["scene"]
    label = "Status"

    def GetStatusByName(self, name):
        statuses = ftrack.getTaskStatuses()

        result = None
        for s in statuses:
            if s.get("name").lower() == name.lower():
                result = s

        return result

    def process(self, context, instance):

        task = ftrack.Task(context.data("ftrackData")["Task"]["id"])

        if task.getStatus().getName().lower() != "in progress":
            task.setStatus(self.GetStatusByName("in progress"))
