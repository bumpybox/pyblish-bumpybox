import os

#import pyblish.api
#import nuke

drafts_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
drafts_path = os.path.dirname(os.path.dirname(os.path.dirname(drafts_path)))
drafts_path = os.path.join(drafts_path, 'deadline', 'draft-templates')


@pyblish.api.log
class ExtractDeadline(pyblish.api.Extractor):
    """ Gathers optional Nuke related data for Deadline
    """

    families = ['deadline.render']
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
            path = os.path.join(drafts_path, 'MJPEG_full_linearTo2.2.py')
            extra_info_key_value['DraftTemplates0'] = path

        # only for the call up project
        if ftrack_data['Project']['code'] == 'the_call_up':
            path = os.path.join(drafts_path, 'MPEG4_full_alexaToSRGB.py')
            extra_info_key_value['DraftTemplates0'] = path
            path = os.path.join(drafts_path, 'DNXHD_1080_alexaToSRGB_32mb.py')
            extra_info_key_value['DraftTemplates1'] = path

        job_data['ExtraInfoKeyValue'] = extra_info_key_value

        instance.set_data('deadlineJobData', value=job_data)

        components = {str(instance): {}}
        instance.set_data('ftrackComponents', value=components)
