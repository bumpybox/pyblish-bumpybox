from pyblish import api
from pyblish_bumpybox import inventory


class RepairPointsAction(api.Action):
    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):
        import pymel.core as pm

        # Get the errored instances
        failed = []
        for result in context.data["results"]:
            if (result["error"] is not None and result["instance"] is not None
               and result["instance"] not in failed):
                failed.append(result["instance"])

        # Apply pyblish.logic to get the instances for the plug-in
        instances = api.instances_by_plugin(failed, plugin)

        for instance in instances:
            for node in instance[0].members():
                pm.delete(pm.cluster(node))


class ValidatePoints(api.InstancePlugin):
    """ Ensures all points in mesh are zero"ed out """

    families = ["mayaAscii", "mayaBinary", "alembic"]
    label = "Points"
    order = inventory.get_order(__file__, "ValidatePoints")
    actions = [RepairPointsAction]
    optional = True
    targets = ["process.local"]

    def process(self, instance):

        for node in instance[0].members():
            for p in node.getShape().pnts:
                position = 0
                position += p.pntx.get()
                position += p.pnty.get()
                position += p.pntz.get()

                msg = "Points aren't zero'ed out on: %s" % p
                assert position < 0.00001, msg
