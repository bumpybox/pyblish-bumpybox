import os

import pymel
import pyblish.api
from pyblish_bumpybox.plugins.maya import utils
reload(utils)


class RepairRenderSettings(pyblish.api.Action):

    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):

        render_globals = pymel.core.PyNode('defaultRenderGlobals')

        # repairing current render layer
        layer = pymel.core.PyNode('defaultRenderLayer')
        pymel.core.nodetypes.RenderLayer.setCurrent(layer)

        # repairing frame/animation ext
        render_globals.animation.set(1)
        render_globals.outFormatControl.set(0)
        render_globals.putFrameBeforeExt.set(1)
        render_globals.extensionPadding.set(4)
        render_globals.periodInExt.set(1)

        # repairing frame padding
        render_globals.extensionPadding.set(4)

        # repairing file name prefix
        filename = os.path.basename(context.data('currentFile'))
        filename = os.path.splitext(filename)[0]
        expected_prefix = '<RenderLayer>/%s' % filename
        render_globals.imageFilePrefix.set(expected_prefix)

        # repairing renderpass naming
        render_globals.multiCamNamingMode.set(1)
        render_globals.bufferName.set('<RenderPass>')

        # repairing workspace path
        path = os.path.dirname(pymel.core.system.sceneName())
        pymel.core.system.Workspace.open(path)

        # repairing default lighting
        render_globals.enableDefaultLight.set(False)

        # repairing image path
        output = utils.get_path(context).replace('\\', '/')
        pymel.core.system.Workspace.fileRules['images'] = output
        pymel.core.system.Workspace.save()

        # repairing project directory
        project_path = utils.get_project_path(context,
                                              self.log).replace('\\', '/')
        pymel.core.mel.eval(' setProject "%s"' % project_path)


class ValidateRenderSettings(pyblish.api.InstancePlugin):
    """ Validates settings """

    order = pyblish.api.ValidatorOrder
    families = ['deadline.render']
    optional = True
    label = 'Render Settings'
    actions = [RepairRenderSettings]

    def process(self, instance):

        # adding check for other instances to pass
        if 'ValidateRenderSettings' not in instance.context.data:
            instance.context.data['ValidateRenderSettings'] = True
        else:
            return

        render_globals = pymel.core.PyNode('defaultRenderGlobals')

        # validate frame/animation ext
        msg = 'Frame/Animation ext is incorrect. Expected: "name.#.ext".'
        assert render_globals.animation.get() == 1, msg
        assert render_globals.outFormatControl.get() == 0, msg
        assert render_globals.putFrameBeforeExt.get() == 1, msg
        assert render_globals.extensionPadding.get() == 4, msg
        assert render_globals.periodInExt.get() == 1, msg

        # validate frame padding
        msg = 'Frame padding is incorrect. Expected: 4'
        assert render_globals.extensionPadding.get() == 4, msg

        # validate file name prefix
        msg = 'File name prefix is incorrect.'
        prefix = render_globals.imageFilePrefix.get()
        filename = os.path.basename(instance.context.data('currentFile'))
        filename = os.path.splitext(filename)[0]
        expected_prefix = '<RenderLayer>/%s' % filename
        assert prefix == expected_prefix, msg

        # validate current render layer
        msg = 'Current layer needs to be "masterLayer"'
        currentLayer = pymel.core.nodetypes.RenderLayer.currentLayer()
        assert currentLayer == 'defaultRenderLayer', msg

        # validate workspace path
        path = os.path.dirname(pymel.core.system.sceneName())
        workspace_path = pymel.core.system.Workspace.getPath()
        msg = 'Current workspace is not next to the work file.'
        assert path == workspace_path, msg

        # validate default lighting off
        msg = 'Default lighting is enabled.'
        assert not render_globals.enableDefaultLight.get(), msg

        # ftrack dependent validation
        if not instance.context.has_data('ftrackData'):
            return

        # validate image path
        expected_output = utils.get_path(instance.context).replace('\\', '/')
        paths = [str(pymel.core.system.Workspace.getPath().expand())]
        paths.append(str(pymel.core.system.Workspace.fileRules['images']))
        output = os.path.join(*paths)

        msg = 'Project Images directory is incorrect.'
        msg += ' Expected: %s' % expected_output
        self.log.info(expected_output)
        assert output == expected_output, msg

        # validate project directory
        project_path = utils.get_project_path(instance.context,
                                              self.log).replace('\\', '/')
        scene_project = pymel.core.system.Workspace.getPath().expand()
        scene_project = scene_project.replace('\\', '/')

        msg = 'Project path is incorrect.'
        msg += '\n\nCurrent: %s' % scene_project
        msg += '\n\nExpected: %s' % project_path
        assert project_path == scene_project, msg

        """
        # validate renderpass naming
        msg = 'Renderpass naming is incorrect:'
        msg += '\n\n"Frame Buffer Naming": "Custom"'
        msg += '\n\n"Custom Naming String": "<RenderPass>"'
        data = instance.data('data')
        if 'multiCamNamingMode' in data:
            assert int(data['multiCamNamingMode']) == 1, msg
            assert render_globals.bufferName.get() == '<RenderPass>', msg
        """
