import pyblish.api


class RepairMantraSettings(pyblish.api.Action):

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

        # Apply pyblish.logic to get the instances for the plug-in
        instances = pyblish.api.instances_by_plugin(failed, plugin)

        for instance in instances:

            # background vs. foreground rendering
            soho_foreground = 1
            if (instance.data["family"].endswith("ifd") or
               instance.data["family"].startswith("img.farm")):
                soho_foreground = 0

            # setting parms
            instance[0].setParms({"soho_foreground": soho_foreground})


class ValidateMantraSettings(pyblish.api.InstancePlugin):
    """ Validates mantra settings """

    families = ["img.*"]
    order = pyblish.api.ValidatorOrder
    label = "Mantra Settings"
    actions = [RepairMantraSettings]
    optional = True

    def process(self, instance):

        node = instance[0]

        # igonore local ifds
        if instance.data["family"] == "img.local.ifd":
            return

        # When rendering locally we need to block, so Pyblish doesn"t execute
        # other plugins. When render on a farm, the block needs to be lifted.
        if instance.data["family"].startswith("img.farm"):
            msg = "Mantra needs to render in the background for farm "
            msg += "rendering. Disable \"Block Until Render Complete\" in "
            msg += "\"Driver\"."
            assert not node.parm("soho_foreground").eval(), msg
        else:
            msg = "Mantra needs to render in the foreground for local "
            msg += "rendering. Enable \"Block Until Render Complete\" in "
            msg += "\"Driver\"."
            assert node.parm("soho_foreground").eval(), msg
