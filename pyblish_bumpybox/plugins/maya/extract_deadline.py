import os
import shutil

import pyblish.api
import pymel
import pipeline_schema


class ExtractDeadline(pyblish.api.InstancePlugin):
    """ Gathers optional Maya related data for Deadline
    """

    order = pyblish.api.ExtractorOrder
    families = ['deadline.render']
    label = 'Maya to Deadline'

    def process(self, instance):

        # getting job data
        job_data = {}
        if instance.has_data('deadlineData'):
            job_data = instance.data('deadlineData')['job'].copy()
            plugin_data = instance.data('deadlineData')['plugin'].copy()

        # setting optional data
        job_data['Pool'] = 'medium'

        drg = pymel.core.PyNode('defaultRenderGlobals')
        if drg.currentRenderer.get() == 'arnold':
            job_data['LimitGroups'] = 'arnold'

        job_data['Group'] = 'maya_%s' % pymel.versions.flavor()

        components = {str(instance): {}}
        instance.set_data('ftrackComponents', value=components)

        current_file = instance.context.data('currentFile')
        render_dir = os.path.join(os.path.dirname(current_file), 'render')

        # create publish directory
        if not os.path.exists(render_dir):
            os.makedirs(render_dir)

        # copy work file to render
        render_file = os.path.basename(current_file)
        render_file = os.path.join(render_dir, render_file)
        plugin_data["SceneFile"] = render_file

        if not instance.context.has_data('deadlineRenderSave'):
            shutil.copy(current_file, render_file)

            instance.context.set_data('deadlineRenderSave', value=True)

        instance.context.set_data('deadlineInput', value=render_file)

        # create render directory
        data = pipeline_schema.get_data()
        data["extension"] = "temp"
        data["output_type"] = "img"
        data["name"] = str(instance)
        expected_output = pipeline_schema.get_path("output_sequence", data)
        expected_output = os.path.dirname(expected_output)

        if not os.path.exists(expected_output):
            os.makedirs(expected_output)

        data = instance.data('deadlineData')
        data['job'] = job_data
        data['plugin'] = plugin_data
        instance.set_data('deadlineData', value=data)


class ExtractRenderFile(pyblish.api.InstancePlugin):
    """ Adds the render file to Ftrack integration
    """

    order = pyblish.api.ExtractorOrder
    families = ['scene']
    label = 'Maya to Ftrack'

    def process(self, instance):
        current_file = instance.context.data('currentFile')
        render_dir = os.path.join(os.path.dirname(current_file), 'render')
        render_file = os.path.basename(current_file)
        render_file = os.path.join(render_dir, render_file)

        if not os.path.exists(render_file):
            components = instance.data['ftrackComponents']
            components['maya_render'] = {'path': render_file}
