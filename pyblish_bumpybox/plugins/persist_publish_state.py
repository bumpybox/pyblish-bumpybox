from pyblish_bumpybox import plugin


class PersistPublishState(plugin.ContextPlugin):
    """Extracts the publish state of all instances

    Instances needs to have a "instanceToggled" method stored as data member.
    """

    order = plugin.ValidatorOrder
    targets = ["default", "process"]
    label = "Publish State"

    def process(self, context):

        for instance in context:
            if "instanceToggled" not in instance.data.keys():
                continue
            self.log.info(instance)
            self.log.info(instance.data)
            instance.data["instanceToggled"](
                instance, instance.data["publish"]
            )
