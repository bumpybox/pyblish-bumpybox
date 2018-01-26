from pyblish_bumpybox import plugin


class ValidateUniqueCompRenders(plugin.ContextPlugin):

    order = plugin.ValidatorOrder
    label = "Unique Comp Renders"
    families = ["img.local.*"]

    def process(self, context):

        instances = plugin.instances_by_plugin(context,
                                                    ValidateAEUniqueCompRenders)

        names = []
        for instance in instances:
            names.append(instance.data["name"])

        msg = "More than one item in the render queue,"
        msg += " are from the same composition"
        assert len(names) == len(set(names)), msg
