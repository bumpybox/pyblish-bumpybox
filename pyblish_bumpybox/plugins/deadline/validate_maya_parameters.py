from pyblish import api
from pyblish_bumpybox import inventory


class RepairParametersAction(api.Action):

    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):
        import pymel.core

        # Get the errored instances
        failed = []
        for result in context.data["results"]:
            if (result["error"] is not None and
               result["instance"] is not None and
               result["instance"] not in failed):
                failed.append(result["instance"])

        # Apply pyblish.logic to get the instances for the plug-in.
        instances = plugin.instances_by_plugin(failed, plugin)

        plugin = plugin()
        for instance in instances:

            node = instance[0]

            if not hasattr(node, "deadlineChunkSize"):
                pymel.core.addAttr(node,
                                   longName="deadlineChunkSize",
                                   defaultValue=1,
                                   attributeType="long")
                attr = pymel.core.Attribute(node.name() + ".deadlineChunkSize")
                pymel.core.setAttr(attr, channelBox=True)

            if not hasattr(node, "deadlinePriority"):
                pymel.core.addAttr(node,
                                   longName="deadlinePriority",
                                   defaultValue=50,
                                   attributeType="long")
                attr = pymel.core.Attribute(node.name() + ".deadlinePriority")
                pymel.core.setAttr(attr, channelBox=True)

            if not hasattr(node, "deadlinePool"):
                pymel.core.addAttr(node,
                                   longName="deadlinePool",
                                   dataType="string")
                attr = pymel.core.Attribute(node.name() + ".deadlinePool")
                pymel.core.setAttr(attr, channelBox=True)

            if not hasattr(node, "deadlineConcurrentTasks"):
                pymel.core.addAttr(node,
                                   longName="deadlineConcurrentTasks",
                                   defaultValue=1,
                                   attributeType="long")
                attr = pymel.core.Attribute(
                    node.name() + ".deadlineConcurrentTasks"
                )
                pymel.core.setAttr(attr, channelBox=True)


class ValidateMayaParameters(api.ContextPlugin):
    """ Validates the existence of deadline parameters on node. """

    order = inventory.get_order(__file__, "ValidateMayaParameters")
    label = "Parameters"
    families = ["deadline"]
    hosts = ["maya"]
    actions = [RepairParametersAction]

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
