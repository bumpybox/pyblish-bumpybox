import os

import pyblish.api
import nuke
import pipeline_schema


class RepairRenderSettings(pyblish.api.Action):

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
            node = nuke.toNode(instance.data["name"])

            path = node["file"].value()
            ext = os.path.splitext(path)[-1]

            # repairing the path string
            data = pipeline_schema.get_data()
            data["output_type"] = "img"
            data["name"] = instance.data["name"]

            if ext:
                data["extension"] = ext[1:]
            else:
                data["extension"] = "exr"

            version = 1
            if instance.context.has_data("version"):
                version = instance.context.data("version")
            data["version"] = version

            output = pipeline_schema.get_path("output_sequence", data)

            frame_padding = len(str(int(nuke.root()['last_frame'].value())))
            if frame_padding < 4:
                frame_padding = 4

            padding_string = "%{0}d".format(str(frame_padding).zfill(2))
            output = output.replace("%04d", padding_string)

            node["file"].setValue(output)
            node["file_type"].setValue(os.path.splitext(output)[1][1:])

            if ext == ".exr" or not ext:
                output = os.path.splitext(node["file"].value())[0]
                node["file"].setValue(output + ".exr")
                nuke.updateUI()
                node["compression"].setValue("Zip (1 scanline)")
                node["colorspace"].setValue("default (linear)")
                node["metadata"].setValue("all metadata")

            # making directories
            if not os.path.exists(os.path.dirname(output)):
                os.makedirs(os.path.dirname(output))

            # repairing alpha output
            valid_outputs = ["rgb", "rgba", "all"]
            if node["channels"].value() not in valid_outputs:
                node["channels"].setValue("all")

            # repairing proxy mode
            nuke.root()["proxy"].setValue(False)


class ValidateRenderSettings(pyblish.api.InstancePlugin):
    """ Validates the output path for nuke renders """
    order = pyblish.api.ValidatorOrder
    families = ["deadline.render"]
    label = "Render Output"
    optional = True
    actions = [RepairRenderSettings]

    def process(self, instance):

        path = instance.data["outputPath"]

        node = nuke.toNode(instance.data["name"])
        ext = os.path.splitext(path)[-1]

        data = pipeline_schema.get_data()
        data["output_type"] = "img"
        data["extension"] = ext[1:]
        data["name"] = instance.data["name"]

        version = 1
        if instance.context.has_data("version"):
            version = instance.context.data("version")
        data["version"] = version

        output = pipeline_schema.get_path("output_sequence", data)

        frame_padding = len(str(int(nuke.root()['last_frame'].value())))
        if frame_padding < 4:
            frame_padding = 4

        padding_string = "%{0}d".format(str(frame_padding).zfill(2))
        output = output.replace("%04d", padding_string)

        # validate path
        msg = "Output path is incorrect on: %s" % instance.data["name"]
        msg += " Current: %s" % path.lower()
        msg += " Expected: %s" % output.lower()
        assert path.lower() == output.lower(), msg

        # validate existence
        msg = "Output directory doesn't exist on: %s" % instance.data["name"]
        assert os.path.exists(os.path.dirname(output)), msg

        # validate extension
        msg = "Output extension needs to be \".exr\", \".png\" or \".dpx\","
        msg += " currently \"%s\"" % os.path.splitext(path)[-1]
        assert ext in [".exr", ".png", ".dpx"], msg

        # validate alpha
        msg = "Output channels are wrong."
        valid_outputs = ["rgb", "rgba", "all"]
        assert node["channels"].value() in valid_outputs, msg

        # validate exr settings
        if ext == ".exr":

            # validate compression
            msg = "Compression needs to be \"Zip (1 scanline)\""
            assert node["compression"].value() == "Zip (1 scanline)", msg

            # validate colour space
            msg = "Colour space needs to be \"linear\""
            assert node["colorspace"].value() == "default (linear)", msg

        # validate proxy mode
        msg = "Can't publish with proxy mode enabled."
        assert not nuke.root()["proxy"].value(), msg
