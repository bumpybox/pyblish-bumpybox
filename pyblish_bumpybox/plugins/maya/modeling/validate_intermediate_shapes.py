import pyblish.api
import pymel.core as pm


class RepairIntermediateShapes(pyblish.api.Action):
    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):

        # Get the errored instances
        failed = []
        for result in context.data["results"]:
            if (result["error"] is not None and result["instance"] is not None
               and result["instance"] not in failed):
                failed.append(result["instance"])

        # Apply pyblish.logic to get the instances for the plug-in
        instances = pyblish.api.instances_by_plugin(failed, plugin)

        for instance in instances:
            for node in instance:
                io = pm.ls(node.getShapes(), intermediateObjects=True)
                pm.delete(io)


class ValidateIntermediateShapes(pyblish.api.InstancePlugin):
    """ Ensures there are no intermediate shapes in the scene. """

    families = ['geometry']
    label = 'Intermediate Shapes'
    order = pyblish.api.ValidatorOrder
    actions = [RepairIntermediateShapes]

    def process(self, instance):

        intermediate_objects = []
        for node in instance:
            io = pm.ls(node.getShapes(), intermediateObjects=True)
            intermediate_objects.extend(io)

        msg = 'Intermediate objects present: %s' % intermediate_objects
        assert not intermediate_objects, msg
