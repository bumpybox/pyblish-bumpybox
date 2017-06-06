import nuke

import pyblish.api


class RepairDeadlineNukeParametersAction(pyblish.api.Action):

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

        # Apply pyblish.logic to get the instances for the plug-in.
        instances = pyblish.api.instances_by_plugin(failed, plugin)

        plugin = plugin()
        for instance in instances:

            node = instance[0]
            node.addKnob(nuke.Tab_Knob("Deadline"))

            knob = nuke.Int_Knob("deadlineChunkSize", "Chunk Size")
            knob.setValue(1)
            node.addKnob(knob)

            knob = nuke.Int_Knob("deadlinePriority", "Priority")
            knob.setValue(50)
            node.addKnob(knob)

            knob = nuke.String_Knob("deadlinePool", "Pool")
            node.addKnob(knob)

            knob = nuke.String_Knob("deadlineLimits", "Limits")
            node.addKnob(knob)

            knob = nuke.Int_Knob(
                "deadlineConcurrentTasks", "Concurrent Tasks"
            )
            knob.setValue(1)
            node.addKnob(knob)


class ValidateDeadlineNukeParameters(pyblish.api.InstancePlugin):
    """ Validates the existence of deadline parameters on node. """

    order = pyblish.api.ValidatorOrder
    label = "Parameters"
    families = ["deadline"]
    hosts = ["nuke"]
    actions = [RepairDeadlineNukeParametersAction]

    def process(self, instance):

        node = instance[0]

        msg = "Could not find Chunk Size on node \"{0}\"".format(node)
        assert "deadlineChunkSize" in instance.data, msg

        msg = "Could not find Priority on node \"{0}\"".format(node)
        assert "deadlinePriority" in instance.data, msg

        msg = "Could not find Pool on node \"{0}\"".format(node)
        assert "deadlinePool" in instance.data, msg

        msg = "Could not find Concurrent Tasks on node \"{0}\"".format(node)
        assert "deadlineConcurrentTasks" in instance.data, msg

        msg = "Could not find Limits on node \"{0}\"".format(node)
        assert "deadlineLimits" in instance.data, msg
