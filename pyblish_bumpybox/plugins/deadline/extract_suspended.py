from pyblish import api
from pyblish_bumpybox import inventory


class ExtractSuspended(api.InstancePlugin):
    """ Option to suspend Deadline job on submission """

    order = inventory.get_order(__file__, "ExtractSuspended")
    label = "Suspend Deadline Job Initally"
    families = ["deadline"]
    active = False
    optional = True

    def process(self, instance):

        # getting job data
        job_data = {}
        plugin_data = {}
        if instance.has_data('deadlineData'):
            job_data = instance.data('deadlineData')['job'].copy()
            plugin_data = instance.data('deadlineData')['plugin'].copy()

        job_data["InitialStatus"] = "Suspended"

        instance.data["deadlineData"] = {"job": job_data,
                                         "plugin": plugin_data}
