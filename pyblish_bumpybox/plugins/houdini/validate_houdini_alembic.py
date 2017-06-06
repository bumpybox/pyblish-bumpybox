import pyblish.api


class RepairHoudiniAlembic(pyblish.api.Action):

    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):

        # Get the errored instances
        failed = []
        for result in context.data["results"]:
            if (result["error"] is not None and
               result["instance"] is not None and
               result["instance"] not in failed):
                failed.append(result["instance"])

        # Apply pyblish.logic to get the instances for the plug-in
        instances = pyblish.api.instances_by_plugin(failed, plugin)

        for instance in instances:

            # Setting parameters.
            instance[0].setParms({"partition_mode": 4, "collapse": 1})


class ValidateHoudiniAlembic(pyblish.api.InstancePlugin):
    """ Validates Alembic settings """

    families = ["alembic"]
    order = pyblish.api.ValidatorOrder
    label = "Alembic"
    actions = [RepairHoudiniAlembic]
    optional = True
    hosts = ["houdini"]

    def process(self, instance):

        # Partition mode.
        msg = "Partition mode is not correct. Expected \"Use Combination of "
        msg += "Transform/Shape Node\""
        assert instance[0].parm("partition_mode").eval() == 4, msg

        # Collapse mode.
        msg = "Collapse mode is not correct. Expected \"Collapse Non-Animating"
        msg += " Identity Objects\""
        assert instance[0].parm("collapse").eval() == 1, msg
