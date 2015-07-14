import os

import pymel
import pyblish.api
import ftrack


@pyblish.api.log
class ValidateRenderOutput(pyblish.api.Validator):
    """ Validates settings """

    families = ['deadline.render']
    optional = True
    label = 'Render Output'

    def get_project_path(self, instance):
        # get ftrack data
        ftrack_data = instance.context.data('ftrackData')
        project = ftrack.Project(id=ftrack_data['Project']['id'])
        root_dir = ftrack_data['Project']['root']
        seq_name = ftrack_data['Sequence']['name']
        shot_name = ftrack_data['Shot']['name']
        task_name = ftrack_data['Task']['name']
        task_name_convert = task_name.replace(' ', '_').lower()

        # get version data
        version = 1
        if instance.context.has_data('version'):
            version = instance.context.data('version')
        version_string = 'v%s' % str(version).zfill(3)

        file_name = '.'.join([shot_name, task_name_convert,
                             version_string, 'mb'])
        file_path = os.path.join(root_dir, 'sequences', seq_name, shot_name,
                                 task_name_convert)

        return file_path

    def get_path(self, instance):
        ftrack_data = instance.context.data('ftrackData')
        shot_name = ftrack_data['Shot']['name']
        project = ftrack.Project(id=ftrack_data['Project']['id'])
        root = project.getRoot()
        file_name = os.path.basename(instance.context.data('currentFile'))
        file_name = os.path.splitext(file_name)[0]
        task_name = ftrack_data['Task']['name'].replace(' ', '_').lower()
        version_number = instance.context.data('version')
        version_name = 'v%s' % (str(version_number).zfill(3))

        output = os.path.join(root, 'renders', 'img_sequences', shot_name,
                                task_name, version_name)
        return output

    def process(self, instance):

        # skipping the call up project
        ftrack_data = instance.context.data('ftrackData')
        if ftrack_data['Project']['code'] == 'the_call_up':
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
        msg = 'File name prefix is incorrect. Expected no modification.'
        assert render_globals.imageFilePrefix.get() == '', msg

        # validate image path
        expected_output = self.get_path(instance).replace('\\', '/')
        paths = [str(pymel.core.system.Workspace.getPath().expand())]
        paths.append(str(pymel.core.system.Workspace.fileRules['images']))
        output = os.path.join(*paths)

        msg = 'Project Images directory is incorrect.'
        msg += ' Expected: %s' % expected_output
        assert output == expected_output, msg

        # validate project directory
        project_path = self.get_project_path(instance)
        scene_project = pymel.core.system.Workspace.getPath().expand()

        msg = 'Project path is incorrect. Expected: %s' % project_path
        assert project_path == scene_project, msg

        # validate frame range
        task = ftrack.Task(ftrack_data['Task']['id'])
        project = task.getParents()[-1]
        shot = task.getParent()

        local_first_frame = render_globals.startFrame.get()

        online_first_frame = shot.getFrameStart()

        msg = 'First frame is incorrect.'
        msg += '\n\nLocal last frame: %s' % local_first_frame
        msg += '\n\nOnline last frame: %s' % online_first_frame
        assert local_first_frame == online_first_frame, msg

        local_last_frame = render_globals.endFrame.get()

        online_last_frame = shot.getFrameEnd()

        msg = 'Last frame is incorrect.'
        msg += '\n\nLocal last frame: %s' % local_last_frame
        msg += '\n\nOnline last frame: %s' % online_last_frame
        assert local_last_frame == online_last_frame, msg

    def repair(self, instance):

        render_globals = pymel.core.PyNode('defaultRenderGlobals')
        ftrack_data = instance.context.data('ftrackData')

        # repairing frame/animation ext
        render_globals.animation.set(1)
        render_globals.outFormatControl.set(0)
        render_globals.putFrameBeforeExt.set(1)
        render_globals.extensionPadding.set(4)
        render_globals.periodInExt.set(1)

        # repairing frame padding
        render_globals.extensionPadding.set(4)

        # repairing file name prefix
        render_globals.imageFilePrefix.set('')

        # repairing image path
        output = self.get_path(instance).replace('\\', '/')
        pymel.core.system.Workspace.fileRules['images'] = output
        pymel.core.system.Workspace.save()

        # repairing project directory
        project_path = self.get_project_path(instance).replace('\\', '/')
        pymel.core.mel.eval(' setProject "%s"' % project_path)

        # repairing frame range
        task = ftrack.Task(ftrack_data['Task']['id'])
        project = task.getParents()[-1]
        shot = task.getParent()

        render_globals.startFrame.set(shot.getFrameStart())
        render_globals.endFrame.set(shot.getFrameEnd())
