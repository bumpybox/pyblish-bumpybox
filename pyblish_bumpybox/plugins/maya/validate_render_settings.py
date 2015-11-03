import os

import pymel
import pyblish.api


class ValidateRenderSettings(pyblish.api.Validator):
    """ Validates settings """

    families = ['deadline.render']
    optional = True
    label = 'Render Settings'

    def get_project_path(self, instance):
        path = []
        filename = []

        # get ftrack data
        ftrack_data = instance.context.data('ftrackData')
        path.append(ftrack_data['Project']['root'])
        child_path = []
        parent = False
        parent_name = ftrack_data['Project']['name']

        try:
            name = ftrack_data['Asset_Build']['name'].replace(' ', '_').lower()
            path.append('library')
            asset_type = ftrack_data['Asset_Build']['type'].lower()
            path.append(asset_type)
            path.append(name)
            parent_name = name
        except:
            self.log.info('No asset build found.')

        try:
            name = ftrack_data['Episode']['name'].replace(' ', '_').lower()
            path.append('episodes')
            child_path.append(name)
            parent = True
            parent_name = name
        except:
            self.log.info('No episode found.')

        try:
            name = ftrack_data['Sequence']['name'].replace(' ', '_').lower()
            child_path.append(name)

            if not parent:
                path.append('sequences')

            parent = True
            parent_name = name
        except:
            self.log.info('No sequences found.')

        try:
            name = ftrack_data['Shot']['name'].replace(' ', '_').lower()
            child_path.append(name)

            if not parent:
                path.append('shots')
            parent_name = name
        except:
            self.log.info('No shot found.')

        path.extend(child_path)

        task_name = ftrack_data['Task']['name'].replace(' ', '_').lower()
        path.append(task_name)

        version = 1
        if instance.context.has_data('version'):
            version = instance.context.data('version')
        version_string = 'v%s' % str(version).zfill(3)

        return os.path.join(*path).replace('\\', '/')

    def get_path(self, instance):
        import ftrack

        ftrack_data = instance.context.data('ftrackData')

        parent_name = None
        try:
            parent_name = ftrack_data['Shot']['name']
        except:
            parent_name = ftrack_data['Asset_Build']['name'].replace(' ', '_')

        project = ftrack.Project(id=ftrack_data['Project']['id'])
        root = project.getRoot()
        task_name = ftrack_data['Task']['name'].replace(' ', '_').lower()
        version_number = instance.context.data('version')
        version_name = 'v%s' % (str(version_number).zfill(3))

        path = [root, 'renders', 'img_sequences']

        task = ftrack.Task(ftrack_data['Task']['id'])
        for p in reversed(task.getParents()[:-1]):
            path.append(p.getName())

        path.append(task_name)
        path.append(version_name)

        return os.path.join(*path).replace('\\', '/')

    def process(self, instance, context):

        if context.has_data('renderOutputChecked'):
            return
        else:
            context.set_data('renderOutputChecked', value=True)

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
        filename = os.path.basename(context.data('currentFile'))
        filename = os.path.splitext(filename)[0]
        expected_prefix = '<RenderLayer>/%s' % filename
        assert prefix == expected_prefix, msg

        # validate current render layer
        msg = 'Current layer needs to be "masterLayer"'
        currentLayer = pymel.core.nodetypes.RenderLayer.currentLayer()
        assert currentLayer == 'defaultRenderLayer', msg

        # validate renderpass naming
        msg = 'Renderpass naming is incorrect:'
        msg += '\n\n"Frame Buffer Naming": "Custom"'
        msg += '\n\n"Custom Naming String": "<RenderPass>"'
        data = instance.data('data')
        if 'multiCamNamingMode' in data:
            assert int(data['multiCamNamingMode']) == 1, msg
            assert render_globals.bufferName.get() == '<RenderPass>', msg

        # validate workspace path
        path = os.path.dirname(pymel.core.system.sceneName())
        workspace_path = pymel.core.system.Workspace.getPath()
        msg = 'Current workspace is not next to the work file.'
        assert path == workspace_path, msg

        # validate default lighting off
        msg = 'Default lighting is enabled.'
        assert not render_globals.enableDefaultLight.get(), msg

        # ftrack dependent validation
        if not context.has_data('ftrackData'):
            return

        # validate image path
        expected_output = self.get_path(instance).replace('\\', '/')
        paths = [str(pymel.core.system.Workspace.getPath().expand())]
        paths.append(str(pymel.core.system.Workspace.fileRules['images']))
        output = os.path.join(*paths)

        msg = 'Project Images directory is incorrect.'
        msg += ' Expected: %s' % expected_output
        self.log.info(expected_output)
        assert output == expected_output, msg

        # validate project directory
        project_path = self.get_project_path(instance).replace('\\', '/')
        scene_project = pymel.core.system.Workspace.getPath().expand()
        scene_project = scene_project.replace('\\', '/')

        msg = 'Project path is incorrect.'
        msg += '\n\nCurrent: %s' % scene_project
        msg += '\n\nExpected: %s' % project_path
        assert project_path == scene_project, msg

    def repair(self, instance, context):

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

        # ftrack dependent validation
        if context.has_data('ftrackData'):
            import ftrack
        else:
            return

        # repairing image path
        output = self.get_path(instance).replace('\\', '/')
        pymel.core.system.Workspace.fileRules['images'] = output
        pymel.core.system.Workspace.save()

        # repairing project directory
        project_path = self.get_project_path(instance).replace('\\', '/')
        pymel.core.mel.eval(' setProject "%s"' % project_path)
