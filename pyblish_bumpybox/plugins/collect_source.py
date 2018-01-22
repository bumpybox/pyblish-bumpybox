import pyblish.api


class CollectScene(pyblish.api.ContextPlugin):
    """Collecting the scene from the context."""

    # offset to get latest currentFile from context
    order = pyblish.api.CollectorOrder + 0.1
    label = "Source"
    targets = ["default", "process"]

    def process(self, context):
        import os

        current_file = context.data("currentFile")

        # Skip if current file is directory
        if os.path.isdir(current_file):
            return

        # create instance
        instance = context.create_instance(name=os.path.basename(current_file))

        instance.data["families"] = ["scene"]
        instance.data["family"] = "source"
        instance.data["path"] = current_file
        label = "{0} - source".format(os.path.basename(current_file))
        instance.data["label"] = label
