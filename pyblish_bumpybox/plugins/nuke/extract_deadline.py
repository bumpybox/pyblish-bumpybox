import os

import pyblish.api
import nuke


class ExtractDeadline(pyblish.api.Extractor):
    """ Gathers optional Nuke related data for Deadline
    """

    families = ['deadline.render']
    label = 'Deadline'

    def process(self, instance):

        # getting job data
        job_data = {}
        if instance.has_data('deadlineData'):
            job_data = instance.data('deadlineData')['job'].copy()

        # setting optional data
        job_data['Pool'] = 'medium'
        job_data['ChunkSize'] = '10'
        job_data['LimitGroups'] = 'nuke'

        group = 'nuke_%s' % nuke.NUKE_VERSION_STRING.split('.')[0]
        job_data['Group'] = group

        instance.set_data('deadlineJobData', value=job_data)

        # setting extra info key values
        extra_info_key_value = {}
        if 'ExtraInfoKeyValue' in job_data:
            extra_info_key_value = job_data['ExtraInfoKeyValue']

        args = '-codec mjpeg -q:v 0 -vf lutrgb=r=gammaval(0.45454545):'
        args += 'g=gammaval(0.45454545):b=gammaval(0.45454545)'
        extra_info_key_value['FFMPEGOutputArgs0'] = args
        extra_info_key_value['FFMPEGInputArgs0'] = ''
        input_file = job_data['OutputFilename0'].replace('####', '%04d')
        extra_info_key_value['FFMPEGInput0'] = input_file
        output_file = input_file.replace('img_sequences', 'movies')
        output_file = output_file.replace('.%04d', '')
        output_file = os.path.splitext(output_file)[0] + '.mov'
        extra_info_key_value['FFMPEGOutput0'] = output_file

        job_data['ExtraInfoKeyValue'] = extra_info_key_value

        data = instance.data('deadlineData')
        data['job'] = job_data
        instance.set_data('deadlineData', value=data)

        components = {str(instance): {}}
        instance.set_data('ftrackComponents', value=components)
