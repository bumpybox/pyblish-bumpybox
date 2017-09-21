import nuke
import pyblish.api


class RepairNukeCropAction(pyblish.api.Action):

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

            crop = nuke.nodes.Crop(inputs=[instance[0].input(0)])
            crop["box"].setValue(instance[0].input(0).width(), 2)
            crop["box"].setValue(instance[0].input(0).height(), 3)

            xpos = instance[0].xpos()
            ypos = instance[0].ypos() - 26

            dependent_ypos = instance[0].dependencies()[0].ypos()
            if (instance[0].ypos() - dependent_ypos) <= 51:
                xpos += 110

            crop.setXYpos(xpos, ypos)

            instance[0].setInput(0, crop)


class ValidateNukeCrop(pyblish.api.InstancePlugin):
    """ Validates the existence of crop node before write node. """

    order = pyblish.api.ValidatorOrder
    families = ["write"]
    label = "Crop"
    optional = True
    actions = [RepairNukeCropAction]
    targets = ["process"]

    def process(self, instance):

        msg = "Couldn't find a crop node before %s" % instance
        assert instance[0].dependencies()[0].Class() == "Crop", msg
