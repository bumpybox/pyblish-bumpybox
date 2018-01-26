from pyblish import api
from pyblish_bumpybox import inventory


class ValidateNukeStudioProjectData(api.ContextPlugin):
    """Validate the project data."""

    order = inventory.get_order(__file__, "ValidateNukeStudioProjectData")
    label = "Ftrack Project Data"
    hosts = ["nukestudio"]

    def process(self, context):

        data = context.data["ftrackProjectData"]

        # Validate compulsory data exists
        msg = "No project {0} was found. Please apply a tag to the "
        msg += "sequence called \"ftrack.project\" and add a key called "
        msg += "\"{0}\" with your chosen Ftrack project {0}."

        assert data["project_schema_id"], msg.format("project_schema_id")
        assert data["full_name"], msg.format("full_name")
        assert data["name"], msg.format("name")

        # Validate project_schema_id existence
        project_schema = context.data["ftrackSession"].query(
            "ProjectSchema where id is \"{0}\"".format(
                data["project_schema_id"]
            )
        ).first()

        msg = "Project schema not found. Please create a workflow schema; "
        msg += "http://ftrack.rtd.ftrack.com/en/stable/administering/"
        msg += "managing_workflows/setting_up_workflow_schemas.html,then apply"
        msg += " a tag to the sequence called \"ftrack.project\" and add a key"
        msg += " called \"project_schema_id\" with your chosen Ftrack workflow"
        msg += " schema's id."
        assert project_schema, msg

        # Validate disk_id existence
        disk = context.data["ftrackSession"].query(
            "Disk where id is \"{0}\"".format(
                data["disk_id"]
            )
        ).first()

        msg = "Disk not found. Please create disk; System settings > "
        msg += "Connect Location (legacy) > Disks, then apply a tag to the "
        msg += "sequence called \"ftrack.project\" and add a key called "
        msg += "\"disk_id\" with your chosen projects disk id."
        assert disk, msg
