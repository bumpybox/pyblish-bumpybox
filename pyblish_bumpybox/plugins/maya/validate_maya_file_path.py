import os
import shutil

import pyblish.api


class RepairMayaFilePathAction(pyblish.api.Action):

    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):

        # Get the errored instances
        failed = []
        for result in context.data["results"]:
            if (result["error"] is not None and result["instance"] is not None
               and result["instance"] not in failed):
                failed.append(result["instance"])

        # Apply pyblish.logic to get the instances for the plug-in
        instances = pyblish.api.instances_by_plugin(failed, plugin)

        for instance in instances:

            expected = ValidateMayaFilePath().get_expected_path(
                instance
            )

            if os.path.exists(expected):
                msg = "\"{0}\" already exists. Please repair manually."
                raise ValueError(msg.format(expected))
            else:
                # Create parent directory if it doesn't exist
                if not os.path.exists(os.path.dirname(expected)):
                    os.makedirs(os.path.dirname(expected))

                shutil.copy(instance[0].fileTextureName.get(), expected)
                instance[0].fileTextureName.set(expected)


class ValidateMayaFilePath(pyblish.api.InstancePlugin):
    """ Validate file paths to be in the workspace directory. """

    order = pyblish.api.ValidatorOrder
    families = ["file"]
    label = "File Path"
    actions = [RepairMayaFilePathAction]

    def process(self, instance):

        node = instance[0]
        src = os.path.abspath(node.fileTextureName.get())
        dst = self.get_expected_path(instance)

        msg = "File path is not in workspace directory. Current path: {0}. "
        msg += "Expected path: {1}"
        assert src == dst, msg.format(src, dst)

    def get_expected_path(self, instance):

        return os.path.abspath(
            os.path.join(
                os.path.dirname(instance.context.data["currentFile"]),
                "workspace",
                os.path.basename(instance[0].fileTextureName.get())
            )
        )
