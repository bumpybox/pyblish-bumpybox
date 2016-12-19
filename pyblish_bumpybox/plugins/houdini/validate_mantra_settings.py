import pyblish.api


class BumpyboxHoudiniRepairMantraSettings(pyblish.api.Action):

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
            if "remote" in instance.data["families"]:
                soho_foreground = 0

            # setting parms
            instance[0].setParms({"soho_foreground": soho_foreground})


class BumpyboxHoudiniValidateMantraSettings(pyblish.api.InstancePlugin):
    """ Validates mantra settings """

    families = ["mantra"]
    order = pyblish.api.ValidatorOrder
    label = "Mantra Settings"
    actions = [BumpyboxHoudiniRepairMantraSettings]
    optional = True
    hosts = ["houdini"]

    def process(self, instance):

        node = instance[0]

        # Igonore local ifds
        if ("ifd" in instance.data["families"] and
           "local" in instance.data["families"]):
            return

        # When rendering locally we need to block, so Pyblish doesn"t execute
        # other plugins. When render on a remote, the block needs to be lifted.
        if "remote" in instance.data["families"]:
            msg = "Mantra needs to render in the background for remote "
            msg += "rendering. Disable \"Block Until Render Complete\" in "
            msg += "\"Driver\"."
            assert not node.parm("soho_foreground").eval(), msg
        else:
            msg = "Mantra needs to render in the foreground for local "
            msg += "rendering. Enable \"Block Until Render Complete\" in "
            msg += "\"Driver\"."
            assert node.parm("soho_foreground").eval(), msg
