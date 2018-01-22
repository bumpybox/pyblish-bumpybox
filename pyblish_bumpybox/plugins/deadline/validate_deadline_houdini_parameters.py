import pyblish.api


class RepairDeadlineParametersAction(pyblish.api.Action):

    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):
        import hou

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
            templates = []

            templates.append(hou.IntParmTemplate(
                "deadlineChunkSize", "Chunk Size", 1, default_value=(1,)
            ))
            templates.append(hou.IntParmTemplate(
                "deadlinePriority", "Priority", 1, default_value=(50,)
            ))
            templates.append(hou.StringParmTemplate(
                "deadlinePool", "Pool", 1, default_value=("",)
            ))
            templates.append(hou.IntParmTemplate(
                "deadlineConcurrentTasks",
                "Concurrent Tasks",
                1,
                default_value=(1,)
            ))

            parm_group = node.parmTemplateGroup()
            parm_folder = hou.FolderParmTemplate("folder", "Deadline")

            for template in templates:
                try:
                    parm_folder.addParmTemplate(template)
                except:
                    self.log.debug("Could not add \"{0}\"".format(template))

            parm_group.append(parm_folder)
            node.setParmTemplateGroup(parm_group)


class ValidateDeadlineHoudiniParameters(pyblish.api.InstancePlugin):
    """ Validates the existence of deadline parameters on node. """

    order = pyblish.api.ValidatorOrder
    label = "Parameters"
    families = ["deadline"]
    hosts = ["houdini"]
    actions = [RepairDeadlineParametersAction]

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
