import pyblish.api


class BumpyboxMayaModelingRepairSmoothDisplay(pyblish.api.Action):

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
            for node in instance[0].members():
                node.displaySmoothMesh.set(False)


class BumpyboxMayaModelingValidateSmoothDisplay(pyblish.api.InstancePlugin):
    """ Ensures all meshes are not smoothed """

    order = pyblish.api.ValidatorOrder
    families = ["mayaAscii", "mayaBinary", "alembic"]
    optional = True
    label = "Smooth Display"
    actions = [BumpyboxMayaModelingRepairSmoothDisplay]

    def process(self, instance):

        check = True
        for node in instance[0].members():
            if node.displaySmoothMesh.get():
                msg = "%s has smooth display enabled" % node.name()
                self.log.error(msg)
                check = False

        assert check, "Smooth display enabled meshes in the scene."
