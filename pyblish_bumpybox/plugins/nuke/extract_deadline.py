import os

import pyblish.api
import nuke


class ExtractDeadline(pyblish.api.Extractor):
    """ Gathers optional Nuke related data for Deadline
    """

    families = ['deadline.render']
    label = 'Deadline'

    def frames_to_timecode(self, frames, framerate):

        h = str(int(frames / (3600 * framerate))).zfill(2)
        m = str(int(frames / (60 * framerate) % 60)).zfill(2)
        s = int(float(frames) / framerate % 60)
        f = float('0.' + str((float(frames) / framerate) - s).split('.')[1])
        f = int(f / (1.0 / framerate))

        return '%s:%s:%s:%s' % (h, m, str(s).zfill(2), str(f).zfill(2))

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

        # returning if rendering a single image
        first_frame = instance.data['firstFrame']
        last_frame = instance.data['endFrame']
        if first_frame == last_frame:
            data = instance.data('deadlineData')
            data['job'] = job_data
            instance.set_data('deadlineData', value=data)

            components = {str(instance): {}}
            instance.set_data('ftrackComponents', value=components)

            return

        # setting ffmpeg settings
        extra_info_key_value = {}
        if 'ExtraInfoKeyValue' in job_data:
            extra_info_key_value = job_data['ExtraInfoKeyValue']

        args = '-q:v 0 -pix_fmt yuv420p -vf '
        args += 'scale=trunc(iw/2)*2:trunc(ih/2)*2'
        args += ',colormatrix=bt601:bt709'
        fps = nuke.root()['fps'].value()
        args += ' -timecode %s' % self.frames_to_timecode(first_frame, fps)
        extra_info_key_value['FFMPEGOutputArgs0'] = args

        args = ''
        if os.path.splitext(job_data['OutputFilename0'])[1] == '.exr':
            args += '-gamma 2.2 '
        args += '-framerate %s' % nuke.root()['fps'].value()
        args += ' -start_number %s' % first_frame
        extra_info_key_value['FFMPEGInputArgs0'] = args

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
