import os

import pyblish.api


class BumpyboxHoudiniRepairOutputPath(pyblish.api.Action):

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

        # Apply pyblish.logic to get the instances for the plug-in.
        instances = pyblish.api.instances_by_plugin(failed, plugin)

        plugin = plugin()
        for instance in instances:

            node = instance[0]

            for parm in node.parms():
                if parm.name() in plugin.get_supported_parameters():
                    expected = plugin.get_expected_path(instance, parm.name())
                    parm.set(expected)


class BumpyboxHoudiniValidateOutputPath(pyblish.api.InstancePlugin):
    """ Validates parameter for output """

    families = ["alembic", "mantra", "geometry", "dynamics"]
    order = pyblish.api.ValidatorOrder
    label = "Output Path"
    actions = [BumpyboxHoudiniRepairOutputPath]
    optional = True
    hosts = ["houdini"]

    def get_supported_parameters(self):

        return ["vm_picture", "soho_diskfile", "filename", "sopoutput",
                "dopoutput", "vm_dsmfilename", "vm_dcmfilename"]

    def process(self, instance):

        # All instances has to have a collection.
        msg = "No collection was found on instance \"{0}\"."
        assert instance.data["collection"], msg.format(instance.data["name"])

        # Validate all supported output parameters
        for parm in instance[0].parms():
            if parm.name() in self.get_supported_parameters():
                expected = self.get_expected_path(instance, parm.name())
                current = parm.unexpandedString()

                msg = "Output path for parameter \"{0}\"."
                msg += "Current: \"{1}\". Expected: \"{2}\""
                assert current == expected, msg.format(
                    parm.name(), current, expected
                )

    def get_expected_path(self, instance, parameter_name):

        output = instance[0].parm(parameter_name).eval()

        # Get extension
        ext = os.path.splitext(output)[1]
        # Special case for *.bgeo.sc files since it was two "extensions".
        if output.endswith(".bgeo.sc"):
            ext = ".bgeo.sc"

        # Default padding starting at 4 digits.
        padding = 4
        if instance.data["collection"]:
            padding = instance.data["collection"].padding
        # Can't have less than 4 digits.
        if padding < 4:
            padding = 4

        # File path needs formatting to lower case start, because
        # hou.hipFile.path(), used in currentFile, return lower case.
        root = "${hip}/workspace/${HIPNAME}"

        # Generate padding string
        padding_string = ".$F{0}".format(padding)

        return "{0}_{1}_{2}{3}{4}".format(
            root, instance.data["name"], parameter_name, padding_string, ext
        )
