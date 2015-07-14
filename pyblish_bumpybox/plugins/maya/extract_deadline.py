import pyblish.api

import pymel


@pyblish.api.log
class ExtractDeadline(pyblish.api.Extractor):
    """ Gathers optional Maya related data for Deadline
    """

    families = ['deadline.render']

    def process(self, instance):

        # getting job data
        job_data = {}
        if instance.has_data('deadlineJobData'):
            job_data = instance.data('deadlineJobData').copy()

        # setting optional data
        job_data['Pool'] = 'medium'

        drg = pymel.core.PyNode('defaultRenderGlobals')
        if drg.currentRenderer.get() == 'arnold':
            job_data['LimitGroups'] = 'arnold'

        job_data['Group'] = 'maya_%s' % pymel.versions.flavor()

        instance.set_data('deadlineJobData', value=job_data)

        components = {str(instance): {}}
        instance.set_data('ftrackComponents', value=components)
