import pyblish.api


class ValidateUniqueCompRenders(pyblish.api.ContextPlugin):

    order = pyblish.api.ValidatorOrder
    label = "Unique Comp Renders"
    families = ["img.local.*"]

    def process(self, context):

        instances = pyblish.api.instances_by_plugin(context,
                                                    ValidateUniqueCompRenders)

        names = []
        for instance in instances:
            names.append(str(instance))

        msg = "More than one item in the render queue,"
        msg += " are from the same composition"
        assert len(names) == len(set(names)), msg
