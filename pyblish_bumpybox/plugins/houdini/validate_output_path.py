import os

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

            root = "${hip}/${HIPNAME}"

            padding_string = ".$F4"
            if (instance.data["family"].endswith("alembic") and
               "$F" not in instance.data["originalOutputPath"]):
                padding_string = ""

            path = instance.data["originalOutputPath"]
            ext = os.path.splitext(path)[1]
            if path.endswith(".bgeo.sc"):
                ext = ".bgeo.sc"

            output_path = "{0}_{1}{2}{3}".format(root, instance.data("name"),
                                                 padding_string, ext)

            # getting parameter name
            parm = ""

            if instance.data["family"].endswith("alembic"):
                parm = "filename"
            if instance.data["family"].endswith("geometry"):
                parm = "sopoutput"
            if instance.data["family"].startswith("render"):
                parm = "soho_diskfile"
            if instance.data["family"].startswith("img"):
                parm = "vm_picture"

            instance[0].setParms({parm: output_path})

            # extra validation for render
            if instance.data["family"].startswith("render"):
                path = instance.data["renderOutputPath"]
                ext = os.path.splitext(path)[1]

                output_path = "{0}_{1}{2}{3}".format(root,
                                                     instance.data("name"),
                                                     padding_string, ext)
                instance[0].setParms({"vm_picture": output_path})


class ValidateOutputPath(pyblish.api.InstancePlugin):
    """ Validates output path """

    families = ["img.*", "render.*", "cache.*"]
    order = pyblish.api.ValidatorOrder
    label = "Output Path"
    actions = [RepairOutputPath]
    optional = True

    def process(self, instance):

        # file path needs formatting to lower case start, because
        # hou.hipFile.path(), used in currentFile, return lower case
        root = "${hip}/${HIPNAME}"

        current = instance.data["originalOutputPath"]

        # all outputs needs to have frame padding, except for alembics as they
        # can contain animation within a single file
        padding_string = ".$F4"
        if (instance.data["family"].endswith("alembic") and
           "$F" not in current):
            padding_string = ""

        path = instance.data["originalOutputPath"]
        ext = os.path.splitext(path)[1]
        if path.endswith(".bgeo.sc"):
            ext = ".bgeo.sc"

        expected = "{0}_{1}{2}{3}".format(root, instance.data("name"),
                                          padding_string, ext)

        msg = "Output path is not correct:"
        msg += "\n\nCurrent: {0}\n\nExpected: {1}"
        assert current == expected, msg.format(current, expected)

        # extra validation for render
        if instance.data["family"].startswith("render"):
            current = instance[0].parm("vm_picture").unexpandedString()

            path = instance[0].parm("vm_picture").unexpandedString()
            ext = os.path.splitext(path)[1]

            expected = "{0}_{1}{2}{3}".format(root, instance.data("name"),
                                              padding_string, ext)

            msg = "Image path is not correct:"
            msg += "\n\nCurrent: {0}\n\nExpected: {1}"
            assert current == expected, msg.format(current, expected)
