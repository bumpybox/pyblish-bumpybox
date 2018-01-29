from pyblish import api
from pyblish_bumpybox import inventory


class PersistPublishState(api.ContextPlugin):
    """Extracts the publish state of all instances

    Instances needs to have a "instanceToggled" method stored as data member.
    """

    order = inventory.get_order(__file__, "PersistPublishState")
    targets = ["default", "process"]
    label = "Publish State"

    def process(self, context):

        for instance in context:
            if "instanceToggled" not in instance.data.keys():
                continue
            instance.data["instanceToggled"](
                instance, instance.data["publish"]
            )
