import os

import pyblish.api
import hiero
from pyblish_bumpybox.plugins.hiero import utils


class ExtractPNG(pyblish.api.Extractor):
    """
    """

    families = ['png']
    label = 'Transcode to PNG'

    def frames_to_timecode(self, frames, framerate):

        h = str(int(frames / (3600 * framerate))).zfill(2)
        m = str(int(frames / (60 * framerate) % 60)).zfill(2)
        s = int(frames / framerate % 60)
        f = str((frames / framerate) - s).split('.')[1]

        return '%s:%s:%s.%s' % (h, m, str(s).zfill(2), f)

    def process(self, instance, context):

        item = instance[0]

        # collecting item info
        fps = item.sequence().framerate().toFloat()
        duration = item.sourceOut() - item.sourceIn() + 1
        duration = self.frames_to_timecode(duration, fps)
        source_in = self.frames_to_timecode(item.sourceIn(), fps)

        # create output path
        output_path = utils.get_path(instance, 'png', self.log)
        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))

        # adding deadline data
        job_data = {'Group': 'ffmpeg','Pool': 'medium', 'Plugin': 'FFmpeg',
                    'OutputFilename0': output_path, 'Frames': 0}

        plugin_data = {'InputArgs0': '', 'OutputFile': output_path,
                            'ReplacePadding': False, 'UseSameInputArgs': False}

        args = '-ss %s' % source_in
        args += ' -t %s' % duration
        plugin_data['OutputArgs'] = args

        input_path = item.source().mediaSource().fileinfos()[0].filename()
        plugin_data['InputFile0'] = input_path

        data = {'job': job_data, 'plugin': plugin_data}
        instance.set_data('deadlineData', value=data)
