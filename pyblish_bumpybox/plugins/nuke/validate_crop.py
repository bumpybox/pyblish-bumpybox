import nuke
import pyblish.api


class RepairCrop(pyblish.api.Action):

    label = 'Repair'
    icon = 'wrench'
    on = 'failed'

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
            node = nuke.toNode(instance.data["name"])

            input = node.input(0)

            crop = nuke.nodes.Crop(inputs=[node.input(0)])
            crop['box'].setValue(input.width(), 2)
            crop['box'].setValue(input.height(), 3)

            node.setInput(0, crop)


class ValidateCrop(pyblish.api.Validator):
    """Validates the existence of crop node before write node
    """

    families = ['deadline.render']
    label = 'Crop Output'
    optional = True
    actions = [RepairCrop]

    def process(self, instance):

        node = nuke.toNode(instance.data["name"])

        msg = "Couldn't find a crop node before %s" % instance
        assert node.dependencies()[0].Class() == 'Crop', msg
