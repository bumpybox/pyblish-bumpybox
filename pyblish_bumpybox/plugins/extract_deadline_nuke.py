import pyblish.api

import nuke


@pyblish.api.log
class ExtractDeadlineNuke(pyblish.api.Extractor):
    """ Gathers optional Nuke related data for Deadline
    """

    families = ['deadline.render']
    hosts = ['nuke']
    version = (0, 1, 0)

    def process_context(self, context):

        # getting job data
        job_data = {}
        if context.has_data('deadlineJobData'):
            job_data = context.data('deadlineJobData').copy()

        # setting optional data
        job_data['Pool'] = 'medium'
        job_data['ChunkSize'] = '10'
        job_data['LimitGroups'] = 'nuke'

        group = 'nuke_%s' % nuke.NUKE_VERSION_STRING.replace('.', '')
        job_data['Group'] = group

        context.set_data('deadlineJobData', value=job_data)
