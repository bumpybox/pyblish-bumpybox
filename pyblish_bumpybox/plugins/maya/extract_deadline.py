import os
import shutil

import pyblish.api
import pymel


class ExtractDeadline(pyblish.api.Extractor):
    """ Gathers optional Maya related data for Deadline
    """

    families = ['deadline.render']
    label = 'Maya to Deadline'

    def process(self, instance, context):

        # getting job data
        job_data = {}
        if instance.has_data('deadlineData'):
            job_data = instance.data('deadlineData')['job'].copy()

        # setting optional data
        job_data['Pool'] = 'medium'

        drg = pymel.core.PyNode('defaultRenderGlobals')
        if drg.currentRenderer.get() == 'arnold':
            job_data['LimitGroups'] = 'arnold'

        job_data['Group'] = 'maya_%s' % pymel.versions.flavor()

        data = instance.data('deadlineData')
        data['job'] = job_data
        instance.set_data('deadlineData', value=data)

        components = {str(instance): {}}
        instance.set_data('ftrackComponents', value=components)

        current_file = context.data('currentFile')
        render_dir = os.path.join(os.path.dirname(current_file), 'render')

        # create publish directory
        if not os.path.exists(render_dir):
            os.makedirs(render_dir)

        # copy work file to render
        render_file = os.path.basename(current_file)
        render_file = os.path.join(render_dir, render_file)

        if not os.path.exists(render_file):
            shutil.copy(current_file, render_file)

        context.set_data('deadlineInput', value=render_file)
