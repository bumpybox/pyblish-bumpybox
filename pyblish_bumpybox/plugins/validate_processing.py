from pyblish_bumpybox import plugin


class ValidateProcessing(plugin.ContextPlugin):
    """Validates whether there are any instances to process."""

    order = plugin.ValidatorOrder
    optional = True
    label = "Data to Process"
    targets = ["default", "process"]
    hosts = ["nuke", "nukeassist", "maya"]

    def process(self, context):

        instances_to_process = []
        instance_labels = ""
        for instance in context:

            # Ignore source family
            families = instance.data.get("families", [])
            families += [instance.data["family"]]
            if "source" in families:
                continue

            instance_labels += "\n\n" + instance.data.get("label", "name")

            if instance.data("publish", True):
                instances_to_process.append(instance)

        msg = (
            "No nodes were enabled for processing. Please hit reset and choose"
            " a node to process in the left-hand list.\n\nPossible nodes to "
            "process:{0}".format(instance_labels)
        )
        assert instances_to_process, msg
