import pyblish.api


@pyblish.api.log
class ExtractDeadlineDraftCustom(pyblish.api.Extractor):
    """ Gathers optional Draft related data for Deadline
    """

    order = pyblish.api.Extractor.order + 0.1
    families = ['deadline.render']
    hosts = ['*']
    version = (0, 1, 0)

    def process_context(self, context):

        # getting job data
        job_data = {}
        if context.has_data('deadlineJobData'):
            job_data = context.data('deadlineJobData').copy()

        # setting extra info key values
        extra_info_key_value = {}
        if 'ExtraInfoKeyValue' in job_data:
            extra_info_key_value = job_data['ExtraInfoKeyValue']

        t = ''
        if context.data('ftrackData')['project']['code'] == 'the_call_up':
            t = r'K:/tools/Deadline/draft-templates/quicktime_MPEG4_and_DNxHD.py'
        extra_info_key_value['DraftTemplate'] = t

        context.set_data('deadlineJobData', value=job_data)
