import nuke

import pyblish.api


class BumpyboxRoyalRenderRepairParameters(pyblish.api.Action):

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
            node.addKnob(nuke.Tab_Knob("RoyalRender"))

            knob = nuke.Int_Knob("royalRenderPriority", "Priority")
            knob.setValue(50)
            node.addKnob(knob)


class BumpyboxRoyalRenderValidateNukeParameters(pyblish.api.InstancePlugin):
    """ Validates the existence of deadline parameters on node. """

    order = pyblish.api.ValidatorOrder
    label = "Parameters"
    families = ["royalrender"]
    hosts = ["nuke"]
    actions = [BumpyboxRoyalRenderRepairParameters]

    def process(self, instance):

        node = instance[0]

        msg = "Could not find Priority on node \"{0}\"".format(node)
        assert "royalRenderPriority" in instance.data, msg
