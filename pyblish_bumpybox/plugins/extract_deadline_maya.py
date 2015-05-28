import pyblish.api

import pymel


@pyblish.api.log
class ExtractDeadlineMaya(pyblish.api.Extractor):
    """ Gathers optional Maya related data for Deadline
    """

    families = ['deadline.render']
    hosts = ['maya']
    version = (0, 1, 0)

    def process_context(self, context):

        # getting job data
        job_data = {}
        if context.has_data('deadlineJobData'):
            job_data = context.data('deadlineJobData').copy()

        # setting optional data
        job_data['Pool'] = 'medium'

        drg = pymel.core.PyNode('defaultRenderGlobals')
        if drg.currentRenderer.get() == 'arnold'
            job_data['LimitGroups'] = 'arnold'

        job_data['Group'] = 'maya_%s' % pymel.versions.flavor()

        context.set_data('deadlineJobData', value=job_data)
