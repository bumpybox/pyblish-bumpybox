import os

import pyblish.api
import pyblish_ftrack
import pyblish_deadline


class BumpyboxDeadlineExtractEnvironment(pyblish.api.InstancePlugin):
    """ Appending Ftrack enviroment variables to Deadline job. """

    order = pyblish.api.ExtractorOrder
    families = ["deadline"]
    label = "Environment"

    def process(self, instance):

        # Get plugin and job data.
        data = instance.data.get("deadlineData", {"job": {}, "plugin": {}})

        key = "FTRACK_SERVER={0}".format(os.environ["FTRACK_SERVER"])
        data["job"]["EnvironmentKeyValue0"] = key
        key = "FTRACK_APIKEY={0}".format(os.environ["FTRACK_APIKEY"])
        data["job"]["EnvironmentKeyValue1"] = key
        key = "LOGNAME={0}".format(os.environ["LOGNAME"])
        data["job"]["EnvironmentKeyValue2"] = key
        key = "PYTHONPATH={0}".format(os.environ["PYTHONPATH"])
        data["job"]["EnvironmentKeyValue3"] = key
        key = "FTRACK_TEMPLATES_PATH={0}".format(
            os.environ["FTRACK_TEMPLATES_PATH"]
        )
        data["job"]["EnvironmentKeyValue4"] = key
        key = "FTRACK_TASKID={0}".format(os.environ["FTRACK_TASKID"])
        data["job"]["EnvironmentKeyValue5"] = key

        # OnJobFinished
        key = "OnJobFinishedPaths={0}".format(
            os.pathsep.join(
                [
                    os.path.join(
                        os.path.dirname(__file__),
                        "OnJobFinished"
                    ),
                    os.path.join(
                        os.path.dirname(pyblish_ftrack.__file__),
                        "plugins"
                    ),
                    os.path.join(
                        os.path.dirname(__file__),
                        "OnJobFinished"
                    ),
                    os.path.join(
                        os.path.dirname(os.path.dirname(__file__)),
                        "ftrack"
                    )
                ]
            )
        )
        data["job"]["EnvironmentKeyValue6"] = key

        # OnJobSubmitted
        key = "OnJobSubmittedPaths={0}".format(
            os.pathsep.join(
                [
                    os.path.join(
                        os.path.dirname(__file__),
                        "OnJobSubmitted"
                    ),
                    os.path.join(
                        os.path.dirname(pyblish_deadline.__file__),
                        "plugins"
                    )
                ]
            )
        )
        data["job"]["EnvironmentKeyValue7"] = key

        key = "FTRACK_LOCATIONS_MODULE={0}".format(
            os.environ["FTRACK_LOCATIONS_MODULE"]
        )
        data["job"]["EnvironmentKeyValue8"] = key

        instance.data["deadlineData"] = data
