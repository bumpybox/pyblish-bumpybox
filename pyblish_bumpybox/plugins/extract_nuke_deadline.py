import pyblish.api

import nuke


@pyblish.api.log
class ExtractDeadlineNuke(pyblish.api.Extractor):
    """ Gathers optional Nuke related data for Deadline
    """

    families = ['deadline.render']
    hosts = ['nuke']
    version = (0, 1, 0)
    label = 'Nuke to Deadline'

    def process(self, instance):

        # getting job data
        job_data = {}
        if instance.has_data('deadlineJobData'):
            job_data = instance.data('deadlineJobData').copy()

        # setting optional data
        job_data['Pool'] = 'medium'
        job_data['ChunkSize'] = '10'
        job_data['LimitGroups'] = 'nuke'

        group = 'nuke_%s' % nuke.NUKE_VERSION_STRING.replace('.', '')
        job_data['Group'] = group

        instance.set_data('deadlineJobData', value=job_data)

        # skipping instance if ftrackData isn't present
        if not instance.context.has_data('ftrackData'):
            self.log.info('No ftrackData present.')
            return

        ftrack_data = instance.context.data('ftrackData')

        # setting extra info key values
        extra_info_key_value = {}
        if 'ExtraInfoKeyValue' in job_data:
            extra_info_key_value = job_data['ExtraInfoKeyValue']

        # ethel and ernest project
        if ftrack_data['Project']['code'] == 'ethel_and_ernest':
            extra_info_key_value['DraftTemplates0'] = r'K:/tools/Deadline/draft-templates/MJPEG_full_linearTo2.2.py'

        # only for the call up project
        if ftrack_data['Project']['code'] == 'the_call_up':
            extra_info_key_value['DraftTemplates0'] = r'K:/tools/Deadline/draft-templates/MPEG4_full_alexaToSRGB.py'
            extra_info_key_value['DraftTemplates1'] = r'K:/tools/Deadline/draft-templates/DNXHD_1080_alexaToSRGB_32mb.py'

        job_data['ExtraInfoKeyValue'] = extra_info_key_value

        instance.set_data('deadlineJobData', value=job_data)
