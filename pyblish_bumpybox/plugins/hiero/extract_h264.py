import os
import re

import pyblish.api
import hiero
from pyblish_bumpybox.plugins.hiero import utils
reload(utils)


class ExtractH264(pyblish.api.Extractor):

    families = ['h264']
    label = 'Transcode to H264'

    def frames_to_timecode(self, frames, framerate):

        h = str(int(frames / (3600 * framerate))).zfill(2)
        m = str(int(frames / (60 * framerate) % 60)).zfill(2)
        s = int(float(frames) / framerate % 60)
        f = float('0.' + str((float(frames) / framerate) - s).split('.')[1])
        f = int(f / (1.0 / framerate))

        return '%s:%s:%s:%s' % (h, m, str(s).zfill(2), str(f).zfill(2))

    def process(self, instance, context):

        item = instance[0]
        fps = item.sequence().framerate().toFloat()

        # create output path
        output_path = utils.get_path(instance, 'mov', self.log, tag='h264',
                                    sequence=False)
        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))

        # adding deadline data
        job_data = {'Group': 'ffmpeg','Pool': 'medium', 'Plugin': 'FFmpeg',
                    'OutputFilename0': output_path, 'Frames': 0}

        plugin_data = {'OutputFile': output_path, 'ReplacePadding': False,
                        'UseSameInputArgs': False}

        args = '-pix_fmt yuv420p -q:v 0'
        args += ' -timecode %s' % self.frames_to_timecode(item.sourceIn(), fps)
        plugin_data['OutputArgs'] = args

        args = '-ss %s' % (item.sourceIn()/fps)
        args += ' -t %s' % ((item.sourceOut() - item.sourceIn() + 1)/fps)
        plugin_data['InputArgs0'] = args

        input_path = item.source().mediaSource().fileinfos()[0].filename()
        plugin_data['InputFile0'] = input_path

        if instance.has_data('audio'):
            plugin_data['InputFile1'] = instance.data('audio')

        data = {'job': job_data, 'plugin': plugin_data}
        instance.set_data('deadlineData', value=data)
