import os

import pyblish.api
import ftrack
import nuke


class RepairRenderSettings(pyblish.api.Action):

    label = "Repair"
    icon = "wrench"
    on = "failed"

    def get_path(self, instance):
        ftrack_data = instance.context.data("ftrackData")

        parent_name = None
        try:
            parent_name = ftrack_data["Shot"]["name"]
        except:
            parent_name = ftrack_data["Asset_Build"]["name"].replace(" ", "_")

        project = ftrack.Project(id=ftrack_data["Project"]["id"])
        root = project.getRoot()
        file_name = os.path.basename(instance.context.data("currentFile"))
        file_name = os.path.splitext(file_name)[0]
        task_name = ftrack_data["Task"]["name"].replace(" ", "_").lower()
        version_number = instance.context.data("version")
        version_name = "v%s" % (str(version_number).zfill(3))
        filename = ".".join([parent_name, task_name, version_name,
                            "%04d"])

        path = [root, "renders", "img_sequences"]

        task = ftrack.Task(ftrack_data["Task"]["id"])
        for p in reversed(task.getParents()[:-1]):
            path.append(p.getName())

        path.append(task_name)
        path.append(version_name)
        path.append(str(instance))
        path.append(filename)

        return os.path.join(*path).replace("\\", "/")

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
            node = nuke.toNode(str(instance))

            path = node["file"].value()
            ext = os.path.splitext(path)[-1]

            # repairing the path string
            output = self.get_path(instance)
            if ext:
                output = output + ext
            else:
                output = output + ".exr"
            output = output.replace("\\", "/")

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

    def get_path(self, instance):
        ftrack_data = instance.context.data("ftrackData")

        parent_name = None
        try:
            parent_name = ftrack_data["Shot"]["name"]
        except:
            parent_name = ftrack_data["Asset_Build"]["name"].replace(" ", "_")

        project = ftrack.Project(id=ftrack_data["Project"]["id"])
        root = project.getRoot()
        file_name = os.path.basename(instance.context.data("currentFile"))
        file_name = os.path.splitext(file_name)[0]
        task_name = ftrack_data["Task"]["name"].replace(" ", "_").lower()
        version_number = instance.context.data("version")
        version_name = "v%s" % (str(version_number).zfill(3))
        filename = ".".join([parent_name, task_name, version_name,
                            "%04d"])

        path = [root, "renders", "img_sequences"]

        task = ftrack.Task(ftrack_data["Task"]["id"])
        for p in reversed(task.getParents()[:-1]):
            path.append(p.getName())

        path.append(task_name)
        path.append(version_name)
        path.append(str(instance))
        path.append(filename)

        return os.path.join(*path).replace("\\", "/")

    def process(self, instance):

        path = instance.data("deadlineData")["job"]["OutputFilename0"]
        path = path.replace("####", "%04d")

        # on going project specific exception
        ftrack_data = instance.context.data("ftrackData")
        if ftrack_data["Project"]["code"] == "the_call_up":
            msg = "Output directory doesn't exist on: %s" % str(instance)
            assert os.path.exists(os.path.dirname(path)), msg
            return

        node = nuke.toNode(str(instance))
        ext = os.path.splitext(path)[-1]
        output = self.get_path(instance)

        # validate path
        msg = "Output path is incorrect on: %s" % str(instance)
        assert path == (output.replace("\\", "/") + ext), msg

        # validate existence
        msg = "Output directory doesn't exist on: %s" % str(instance)
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
