import os

import pymel
import pyblish.api


class RepairRenderLayerSettings(pyblish.api.Action):

    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):

        render_globals = pymel.core.PyNode("defaultRenderGlobals")

        # Repairing current render layer.
        layer = pymel.core.PyNode("defaultRenderLayer")
        pymel.core.nodetypes.RenderLayer.setCurrent(layer)

        # Repairing masterlayer
        layer.renderable.set(False)

        # Repairing frame/animation extension.
        render_globals.animation.set(1)
        render_globals.outFormatControl.set(0)
        render_globals.putFrameBeforeExt.set(1)
        render_globals.extensionPadding.set(4)
        render_globals.periodInExt.set(1)

        # Repairing frame padding.
        frame_padding = len(str(int(render_globals.endFrame.get())))
        if frame_padding < 4:
            frame_padding = 4
        render_globals.extensionPadding.set(frame_padding)

        # Repairing file name prefix
        expected_prefix = "<RenderLayer>/<Scene>"
        render_globals.imageFilePrefix.set(expected_prefix)

        # Repairing workspace path.
        path = os.path.dirname(pymel.core.system.sceneName())
        pymel.core.system.Workspace.open(path)

        # Repairing image path
        pymel.core.system.Workspace.fileRules["images"] = "workspace"
        pymel.core.system.Workspace.save()

        # Rsepairing project directory
        expected = os.path.join(os.path.dirname(context.data["currentFile"]))
        expected = expected.replace("\\", "/")
        pymel.core.mel.eval("setProject \"{0}\"".format(expected))


class ValidateMayaRenderLayerSettings(pyblish.api.InstancePlugin):
    """ Validates render layer settings. """

    order = pyblish.api.ValidatorOrder
    optional = True
    families = ["renderlayer"]
    label = "Render Layer Settings"
    actions = [RepairRenderLayerSettings]
    hosts = ["maya"]

    def process(self, instance):

        render_globals = pymel.core.PyNode("defaultRenderGlobals")

        # Validate frame/animation extension.
        msg = "Frame/Animation ext is incorrect. Expected: \"name.#.ext\"."
        assert render_globals.animation.get() == 1, msg
        assert render_globals.outFormatControl.get() == 0, msg
        assert render_globals.putFrameBeforeExt.get() == 1, msg
        assert render_globals.periodInExt.get() == 1, msg

        # Frame padding.
        frame_padding = len(str(int(render_globals.endFrame.get())))
        if frame_padding < 4:
            frame_padding = 4
        msg = "Frame padding is incorrect. Expected: {0}".format(frame_padding)
        assert render_globals.extensionPadding.get() == frame_padding, msg

        # Validate file name prefix.
        current = render_globals.imageFilePrefix.get()
        expected = "<RenderLayer>/<Scene>"

        msg = "File name prefix is incorrect. Current: \"{0}\"."
        msg += " Expected: \"{1}\""
        assert expected == current, msg.format(current, expected)

        # Validate current render layer.
        msg = "Current layer needs to be \"masterLayer\""
        currentLayer = pymel.core.nodetypes.RenderLayer.currentLayer()
        assert currentLayer == "defaultRenderLayer", msg

        # Validate masterLayer is turned off
        msg = "\"masterLayer\" must be turned off."
        layer = pymel.core.PyNode("defaultRenderLayer")
        assert not layer.renderable.get(), msg

        # Validate workspace path.
        path = os.path.dirname(pymel.core.system.sceneName()).lower()
        workspace_path = pymel.core.system.Workspace.getPath().lower()
        msg = "Current workspace is not next to the work file."
        assert path == workspace_path, msg

        # Validate image path.
        expected = "workspace"
        current = pymel.core.system.Workspace.fileRules["images"]

        msg = "Project Images path is incorrect. Current: {0}. Expected: {1}"
        assert expected == current, msg.format(current, expected)

        # Validate project directory.
        expected = os.path.dirname(instance.context.data["currentFile"])
        expected = expected.replace("\\", "/")

        current = pymel.core.system.Workspace.getPath().expand()
        current = current.replace("\\", "/")

        msg = "Project path is incorrect. Current: {0}. Expected: {1}"
        assert expected == current, msg.format(current, expected)

        # Validate existence of workspace.mel
        expected = os.path.join(
            os.path.dirname(instance.context.data["currentFile"]),
            "workspace.mel"
        )

        msg = "\"{0}\" does not exist.".format(expected)
        assert os.path.exists(expected), msg
