import pyblish.api


class ValidateProcessing(pyblish.api.ContextPlugin):
    """Validates whether there are any instances to process."""

    order = pyblish.api.ValidatorOrder
    optional = True
    label = "Instance to Process"
    targets = ["process"]

    def process(self, context):

        instances_to_process = []
        for instance in context:
            # Ignore source family
            families = instance.data.get("families", [])
            families += [instance.data["family"]]
            if "source" in families:
                continue

            if instance.data("publish", True):
                instances_to_process.append(instance)

        msg = "No instances enabled for processing."
        assert instances_to_process, msg
