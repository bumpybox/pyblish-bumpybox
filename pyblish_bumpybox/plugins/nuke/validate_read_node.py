from pyblish import api


class RepairReadNodeAction(api.Action):

    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):
        import clique
        import nuke

        # Get the errored instances
        failed = []
        for result in context.data["results"]:
            if (result["error"] is not None and result["instance"] is not None
               and result["instance"] not in failed):
                failed.append(result["instance"])

        # Apply pyblish.logic to get the instances for the plug-in
        instances = plugin.instances_by_plugin(failed, plugin)

        for instance in instances:
            collection = clique.assemble(
                [nuke.filename(instance[0])],
                minimum_items=1,
                patterns=[clique.PATTERNS['frames']]
            )[0][0]

            instance[0]["file"].setValue(
                collection.format("{head}{padding}{tail}")
            )
            instance[0]["first"].setValue(list(collection.indexes)[0])
            instance[0]["last"].setValue(list(collection.indexes)[0])
            instance[0]["origfirst"].setValue(list(collection.indexes)[0])
            instance[0]["origlast"].setValue(list(collection.indexes)[0])


class ValidateReadNode(api.ContextPlugin):
    """Validate Read node is setup correctly."""

    order = api.ValidatorOrder
    families = ["read", "img"]
    match = api.Subset
    label = "Read Node"
    optional = True
    actions = [RepairReadNodeAction]

    def process(self, instance):

        msg = "Read node is not setup correctly."
        assert list(instance.data["collection"].indexes), msg
