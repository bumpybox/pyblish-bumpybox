import pymel.core

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

            if not hasattr(node, "royalRenderPriority"):
                pymel.core.addAttr(node,
                                   longName="royalRenderPriority",
                                   defaultValue=50,
                                   attributeType="long")
                attr = pymel.core.Attribute(
                    node.name() + ".royalRenderPriority"
                )
                pymel.core.setAttr(attr, channelBox=True)


class BumpyboxRoyalRenderValidateMayaParameters(pyblish.api.InstancePlugin):
    """ Validates the existence of deadline parameters on node. """

    order = pyblish.api.ValidatorOrder
    label = "Parameters"
    families = ["royalrender"]
    hosts = ["maya"]
    actions = [BumpyboxRoyalRenderRepairParameters]

    def process(self, instance):

        node = instance[0]

        msg = "Could not find Priority on node \"{0}\"".format(node)
        assert "royalRenderPriority" in instance.data, msg
