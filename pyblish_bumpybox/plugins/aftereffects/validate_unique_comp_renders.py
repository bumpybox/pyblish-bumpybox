from pyblish import api
from pyblish_bumpybox import inventory


class ValidateUniqueCompRenders(api.ContextPlugin):

    order = inventory.get_order(__file__, "ValidateUniqueCompRenders")
    label = "Unique Comp Renders"
    families = ["img.local.*"]

    def process(self, context):

        instances = api.instances_by_plugin(
            context, ValidateAEUniqueCompRenders
        )

        names = []
        for instance in instances:
            names.append(instance.data["name"])

        msg = "More than one item in the render queue,"
        msg += " are from the same composition"
        assert len(names) == len(set(names)), msg
