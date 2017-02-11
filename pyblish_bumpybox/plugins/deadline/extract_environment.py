import os

import pyblish.api


class BumpyboxDeadlineExtractEnvironment(pyblish.api.InstancePlugin):
    """ Appending Ftrack enviroment variables to Deadline job. """

    order = pyblish.api.ExtractorOrder
    families = ["deadline"]
    label = "Environment"

    def process(self, instance):

        # Get plugin and job data.
        data = instance.data.get("deadlineData", {"job": {}, "plugin": {}})

        key_values = {
            "FTRACK_SERVER": os.environ["FTRACK_SERVER"],
            "FTRACK_APIKEY": os.environ["FTRACK_APIKEY"],
            "LOGNAME": os.environ["LOGNAME"],
            "FTRACK_TASKID": os.environ["FTRACK_TASKID"]
        }

        if "EnvironmentKeyValue" in data["job"]:
            data["job"]["EnvironmentKeyValue"].update(key_values)
        else:
            data["job"]["EnvironmentKeyValue"] = key_values

        instance.data["deadlineData"] = data
