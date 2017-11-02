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
            crop = instance[0].dependencies()[0]
            if crop.Class() != "Crop":
                crop = nuke.nodes.Crop(inputs=[instance[0].input(0)])

            crop["box"].setValue(
                (
                    0.0,
                    0.0,
                    instance[0].input(0).width(),
                    instance[0].input(0).height()
                )
            )

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

        crop_node = instance[0].dependencies()[0]
        input_node = crop_node.dependencies()[0]
        expected = (0.0, 0.0, input_node.width(), input_node.height())
        current = crop_node["box"].value()
        msg = (
            "Crop node dimensions; \"{0}\", does not match input "
            "\"{1}\"".format(current, expected)
        )
        assert current == expected, msg
