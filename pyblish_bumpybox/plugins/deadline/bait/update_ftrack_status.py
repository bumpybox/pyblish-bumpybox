from pyblish import api


class UpdateFtrackStatus(api.ContextPlugin):
    """ Updates ftrack status """

    order = api.IntegratorOrder + 0.4

    def process(self, context):
        import os
        import json

        import ftrack

        job = context.data("deadlineJob")
        value = job.GetJobExtraInfoKeyValueWithDefault("PyblishInstanceData",
                                                       "")
        if not value:
            return

        instance_data = json.loads(value)
        version = instance_data["ftrackAssetVersion"]

        if not instance_data["ftrackStatusUpdate"]:
            return

        # since "render" families will always produce a secondary job
        if os.path.splitext(instance_data["family"])[1] in [".ifd"]:
            return

        event = context.data["deadlineEvent"]

        event_dict = {"OnJobSubmitted": "Render Queued",
                      "OnJobStarted": "Render",
                      "OnJobFinished": "Render Complete",
                      "OnJobRequeued": "Render Queued",
                      "OnJobFailed": "Render Failed",
                      "OnJobSuspended": "Render Queued",
                      "OnJobResumed": "Render",
                      "OnJobPended": "Render Queued",
                      "OnJobReleased": "Render Queued"}

        if event in event_dict.keys():

            project_id = context.data["ftrackData"]["Project"]["id"]
            ft_project = ftrack.Project(project_id)
            statuses = ft_project.getVersionStatuses()

            # Need to find the status by name
            ft_status = None
            for status in statuses:
                if status.getName().lower() == event_dict[event].lower():
                    ft_status = status
                    break

            ftrack.AssetVersion(version["id"]).setStatus(ft_status)
            self.log.info("Setting ftrack version to %s" % event_dict[event])
