import pyblish.api


class RepairProjectRoot(pyblish.api.Action):

    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):
        import os

        workspace = os.path.join(
            os.path.dirname(context.data["currentFile"]),
            "workspace"
        ).replace("\\", "/")

        if not os.path.exists(workspace):
            os.makedirs(workspace)

        context.data["activeProject"].setProjectRoot(workspace)


class ValidateHieroNukeStudioProjectRoot(pyblish.api.ContextPlugin):
    """Validate the project root to the workspace directory."""

    order = pyblish.api.ValidatorOrder
    label = "Project Root"
    hosts = ["nukestudio"]
    actions = [RepairProjectRoot]

    def process(self, context):
        import os

        workspace = os.path.join(
            os.path.dirname(context.data["currentFile"]),
            "workspace"
        ).replace("\\", "/")
        project_root = context.data["activeProject"].projectRoot()

        failure_message = (
            'The project root needs to be "{0}", its currently: "{1}"'
        ).format(workspace, project_root)

        assert project_root == workspace, failure_message
