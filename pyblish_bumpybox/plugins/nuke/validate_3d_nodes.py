import pyblish.api


class Repair3dNodes(pyblish.api.Action):

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

            node = instance[0]

            node['read_from_file_link'].setValue(False)


class Validate3dNodes(pyblish.api.Validator):
    """ Makes sure that the 3d nodes are not reading from the disk.
        Reading from disk when opening a nuke script, can cause it to fail.
    """

    families = ['axis', 'camera']
    label = '3D Nodes'
    actions = [Repair3dNodes]

    def process(self, instance):

        node = instance[0]

        msg = '%s has "read from file" enabled.' % node.name()
        assert not bool(node['read_from_file_link'].getValue()), msg
