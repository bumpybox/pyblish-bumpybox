import os

import pymel
import pyblish.api
from pyblish_bumpybox.plugins.maya import utils
reload(utils)
import pipeline_schema


class RepairRenderSettings(pyblish.api.Action):

    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):

        render_globals = pymel.core.PyNode("defaultRenderGlobals")

        # repairing current render layer
        layer = pymel.core.PyNode("defaultRenderLayer")
        pymel.core.nodetypes.RenderLayer.setCurrent(layer)

        # repairing frame/animation ext
        render_globals.animation.set(1)
        render_globals.outFormatControl.set(0)
        render_globals.putFrameBeforeExt.set(1)
        render_globals.extensionPadding.set(4)
        render_globals.periodInExt.set(1)

        # repairing frame padding
        frame_padding = len(str(int(render_globals.endFrame.get())))
        if frame_padding < 4:
            frame_padding = 4
        render_globals.extensionPadding.set(frame_padding)

        # repairing file name prefix
        filename = os.path.basename(context.data("currentFile"))
        filename = os.path.splitext(filename)[0]
        version = "v%s" % str(context.data["version"]).zfill(3)
        expected_prefix = "<RenderLayer>/<RenderLayer>.%s" % version
        render_globals.imageFilePrefix.set(expected_prefix)

        # repairing renderpass naming
        render_globals.multiCamNamingMode.set(1)
        render_globals.bufferName.set("<RenderPass>")

        # repairing workspace path
        path = os.path.dirname(pymel.core.system.sceneName())
        pymel.core.system.Workspace.open(path)

        # repairing default lighting
        render_globals.enableDefaultLight.set(False)

        # repairing image path
        data = pipeline_schema.get_data()
        data["extension"] = "temp"
        data["output_type"] = "img"

        version = 1
        if context.has_data("version"):
            version = context.data("version")
        data["version"] = version

        expected_output = pipeline_schema.get_path("output_sequence", data)
        expected_output = os.path.dirname(os.path.dirname(expected_output))
        pymel.core.system.Workspace.fileRules["images"] = expected_output
        pymel.core.system.Workspace.save()

        # repairing project directory
        data = pipeline_schema.get_data()
        data["extension"] = "mb"

        version = 1
        if context.has_data("version"):
            version = context.data("version")
        data["version"] = version

        project_path = pipeline_schema.get_path("task_work", data)
        project_path = os.path.dirname(project_path).lower()
        pymel.core.mel.eval(" setProject \"%s\"" % project_path)


class ValidateRenderSettings(pyblish.api.InstancePlugin):
    """ Validates settings """

    order = pyblish.api.ValidatorOrder
    families = ["deadline.render"]
    optional = True
    label = "Render Settings"
    actions = [RepairRenderSettings]

    def process(self, instance):

        # adding check for other instances to pass
        if "ValidateRenderSettings" not in instance.context.data:
            instance.context.data["ValidateRenderSettings"] = True
        else:
            return

        render_globals = pymel.core.PyNode("defaultRenderGlobals")

        # validate frame/animation ext
        msg = "Frame/Animation ext is incorrect. Expected: \"name.#.ext\"."
        assert render_globals.animation.get() == 1, msg
        assert render_globals.outFormatControl.get() == 0, msg
        assert render_globals.putFrameBeforeExt.get() == 1, msg
        assert render_globals.periodInExt.get() == 1, msg

        # frame padding
        frame_padding = len(str(int(render_globals.endFrame.get())))
        if frame_padding < 4:
            frame_padding = 4
        msg = "Frame padding is incorrect. Expected: %s" % frame_padding
        assert render_globals.extensionPadding.get() == frame_padding, msg

        # validate file name prefix
        prefix = render_globals.imageFilePrefix.get()
        filename = os.path.basename(instance.context.data("currentFile"))
        filename = os.path.splitext(filename)[0]
        version = "v%s" % str(instance.context.data["version"]).zfill(3)
        expected_prefix = "<RenderLayer>/<RenderLayer>.%s" % version

        msg = "File name prefix is incorrect."
        msg = " Current: %s" % prefix
        msg = " Expected: %s" % expected_prefix
        assert prefix == expected_prefix, msg

        # validate current render layer
        msg = "Current layer needs to be \"masterLayer\""
        currentLayer = pymel.core.nodetypes.RenderLayer.currentLayer()
        assert currentLayer == "defaultRenderLayer", msg

        # validate workspace path
        path = os.path.dirname(pymel.core.system.sceneName()).lower()
        workspace_path = pymel.core.system.Workspace.getPath().lower()
        msg = "Current workspace is not next to the work file."
        assert path == workspace_path, msg

        # validate default lighting off
        msg = "Default lighting is enabled."
        assert not render_globals.enableDefaultLight.get(), msg

        # ftrack dependent validation
        if not instance.context.has_data("ftrackData"):
            return

        # validate image path
        data = pipeline_schema.get_data()
        data["extension"] = "temp"
        data["output_type"] = "img"

        version = 1
        if instance.context.has_data("version"):
            version = instance.context.data("version")
        data["version"] = version

        expected_output = pipeline_schema.get_path("output_sequence", data)
        expected_output = os.path.dirname(os.path.dirname(expected_output))
        paths = [str(pymel.core.system.Workspace.getPath().expand())]
        paths.append(str(pymel.core.system.Workspace.fileRules["images"]))
        output = os.path.join(*paths)

        msg = "Project Images directory is incorrect."
        msg += " Expected: %s" % expected_output
        assert output == expected_output, msg

        # validate project directory
        data = pipeline_schema.get_data()
        data["extension"] = "mb"

        version = 1
        if instance.context.has_data("version"):
            version = instance.context.data("version")
        data["version"] = version

        project_path = pipeline_schema.get_path("task_work", data)
        project_path = os.path.dirname(project_path).lower()
        scene_project = pymel.core.system.Workspace.getPath().expand()
        scene_project = scene_project.replace("\\", "/").lower()

        msg = "Project path is incorrect."
        msg += "\n\nCurrent: %s" % scene_project
        msg += "\n\nExpected: %s" % project_path
        assert project_path == scene_project, msg
