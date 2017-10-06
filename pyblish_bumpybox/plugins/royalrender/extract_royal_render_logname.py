import getpass

import pyblish.api


class ExtractRoyalRenderLogname(pyblish.api.InstancePlugin):
    """Appending RoyalRender data to instances."""

    families = ["royalrender"]
    order = pyblish.api.ExtractorOrder
    label = "Royal Render Logname"
    targets = ["process"]

    def process(self, instance):

        for data in instance.data.get("royalrenderJobs", []):

            submit_params = data.get("SubmitterParameter", [])
            submit_params.append("UserName=0~" + getpass.getuser())
            data["SubmitterParameter"] = submit_params
