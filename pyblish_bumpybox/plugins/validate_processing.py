import pyblish.api


class ValidateProcessing(pyblish.api.ContextPlugin):
    """Validates whether there are any instances to process."""

    order = pyblish.api.ValidatorOrder
    optional = True
    label = "Nodes to Process"
    targets = ["default", "process"]

    def process(self, context):

        instances_to_process = []
        instance_labels = ""
        for instance in context:

            # Ignore source family
            families = instance.data.get("families", [])
            families += [instance.data["family"]]
            if "source" in families:
                continue

            instance_labels += "\n\n" + instance.data["label"]

            if instance.data("publish", True):
                instances_to_process.append(instance)

        msg = (
            "No nodes were enabled for processing. Please hit reset and choose"
            " a node to process in the left-hand list.\n\nPossible nodes to "
            "process:{0}".format(instance_labels)
        )
        assert instances_to_process, msg
