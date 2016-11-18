import os

import pyblish.api


class BumpyboxDeadlineExtractEnvironment(pyblish.api.InstancePlugin):
    """ Appending Ftrack enviroment variables to Deadline job. """

    order = pyblish.api.ExtractorOrder
    families = ["farm"]
    label = "Environment"

    def process(self, instance):

        # Get plugin and job data.
        job_data = {}
        plugin_data = {}
        if instance.has_data('deadlineData'):
            job_data = instance.data('deadlineData')['job'].copy()
            plugin_data = instance.data('deadlineData')['plugin'].copy()

        key = "FTRACK_SERVER={0}".format(os.environ["FTRACK_SERVER"])
        job_data["EnvironmentKeyValue0"] = key
        key = "FTRACK_APIKEY={0}".format(os.environ["FTRACK_ORIGINAL_APIKEY"])
        job_data["EnvironmentKeyValue1"] = key

        instance.data["deadlineData"] = {"job": job_data,
                                         "plugin": plugin_data}
