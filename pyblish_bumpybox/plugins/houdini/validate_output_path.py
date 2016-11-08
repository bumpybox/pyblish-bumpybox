import os

import hou
import pyblish.api


class RepairOutputPath(pyblish.api.Action):

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

            root = "${hip}/workspace/${HIPNAME}"

            frame_padding = instance.data["framePadding"]
            padding_string = ".$F%s" % frame_padding
            # special case for alembics
            if (instance.data["family"].endswith("abc") and
               "$F" not in instance.data["originalOutputPath"]):
                padding_string = ""
            # special case for dynamics
            if instance.data["family"].endswith("sim"):
                padding_string = ".`padzero(%s, $SF)`" % frame_padding

            path = instance.data["originalOutputPath"]
            ext = os.path.splitext(instance.data["family"])[1].replace("_",
                                                                       ".")
            output_path = "{0}_{1}{2}{3}".format(root, instance.data("name"),
                                                 padding_string, ext)

            # getting parameter name
            parm = ""

            if instance[0].type() == hou.nodeType(hou.ropNodeTypeCategory(),
                                                  "alembic"):
                parm = "filename"
            if instance[0].type() == hou.nodeType(hou.ropNodeTypeCategory(),
                                                  "geometry"):
                parm = "sopoutput"

            if instance.data["family"].startswith("img"):
                parm = "vm_picture"
            if instance.data["family"].endswith("ifd"):
                parm = "soho_diskfile"
            if instance.data["family"].endswith("sim"):
                parm = "dopoutput"

            instance[0].setParms({parm: output_path})

            # extra validation for ifd output
            if instance.data["family"].endswith("ifd"):
                path = instance.data["renderOutputPath"]
                ext = os.path.splitext(path)[1]

                output_path = "{0}_{1}{2}{3}".format(root,
                                                     instance.data("name"),
                                                     padding_string, ext)
                instance[0].setParms({"vm_picture": output_path})

            # extra validation for deep data
            if "deepPath" in instance.data and instance.data["deepPath"]:
                ext = os.path.splitext(instance.data["deepPath"])[1]
                path = "{0}_{1}_deep{2}{3}".format(root, instance.data("name"),
                                                   padding_string, ext)

                node = instance[0]
                if node.parm("vm_deepresolver").eval() == "shadow":
                    node.setParms({"vm_dsmfilename": path})
                if node.parm("vm_deepresolver").eval() == "camera":
                    node.setParms({"vm_dcmfilename": path})


class ValidateOutputPath(pyblish.api.InstancePlugin):
    """ Validates output path """

    families = ["img.*", "cache.*"]
    order = pyblish.api.ValidatorOrder
    label = "Output Path"
    actions = [RepairOutputPath]
    optional = True

    def process(self, instance):

        # file path needs formatting to lower case start, because
        # hou.hipFile.path(), used in currentFile, return lower case
        root = "${hip}/workspace/${HIPNAME}"

        current = instance.data["originalOutputPath"]

        frame_padding = instance.data["framePadding"]
        padding_string = ".$F%s" % frame_padding
        # special case for alembics
        if (instance.data["family"].endswith("abc") and
           "$F" not in instance.data["originalOutputPath"]):
            padding_string = ""
        # special case for dynamics
        if instance.data["family"].endswith("sim"):
            padding_string = ".`padzero(%s, $SF)`" % frame_padding

        path = instance.data["originalOutputPath"]
        ext = os.path.splitext(instance.data["family"])[1].replace("_", ".")
        expected = "{0}_{1}{2}{3}".format(root, instance.data("name"),
                                          padding_string, ext)

        msg = "Output path is not correct:"
        msg += "\n\nCurrent: {0}\n\nExpected: {1}"
        assert current == expected, msg.format(current, expected)

        # extra validation for ifd output
        if instance.data["family"].endswith("ifd"):
            current = instance[0].parm("vm_picture").unexpandedString()

            path = instance[0].parm("vm_picture").unexpandedString()
            ext = os.path.splitext(path)[1]

            expected = "{0}_{1}{2}{3}".format(root, instance.data("name"),
                                              padding_string, ext)

            msg = "Image path is not correct:"
            msg += "\n\nCurrent: {0}\n\nExpected: {1}"
            assert current == expected, msg.format(current, expected)

        # extra validation for deep data
        if "deepPath" in instance.data and instance.data["deepPath"]:
            current = instance.data["deepPath"]
            ext = os.path.splitext(instance.data["deepPath"])[1]
            expected = "{0}_{1}_deep{2}{3}".format(root, instance.data("name"),
                                                   padding_string, ext)

            msg = "Deep image path is not correct:"
            msg += "\n\nCurrent: {0}\n\nExpected: {1}"
            assert current == expected, msg.format(current, expected)
