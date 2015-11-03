import os

import pyblish.api
import hiero
from pyblish_bumpybox.plugins.hiero import utils
from pyblish_bumpybox import draft


class ExtractDPX(pyblish.api.Extractor):

    families = ['dpx.trackItem']
    label = 'Transcode to DPX'

    def frames_to_timecode(self, frames, framerate):

        h = str(int(frames / (3600 * framerate))).zfill(2)
        m = str(int(frames / (60 * framerate) % 60)).zfill(2)
        s = int(float(frames) / framerate % 60)
        f = float('0.' + str((float(frames) / framerate) - s).split('.')[1])
        f = int(f / (1.0 / framerate))

        return '%s:%s:%s:%s' % (h, m, str(s).zfill(2), str(f).zfill(2))

    def process(self, instance, context):

        item = instance[0]
        input_path = item.source().mediaSource().fileinfos()[0].filename()
        input_path = input_path.replace('%04d', '####')

        # can only process exrs atm
        msg = 'DPX exporting is only supported from EXRs currently.'
        assert os.path.splitext(input_path)[-1] == '.exr', msg

        # collecting item info
        fps = item.sequence().framerate().toFloat()
        duration = item.sourceOut() - item.sourceIn() + 1
        duration = self.frames_to_timecode(duration, fps)
        source_in = self.frames_to_timecode(item.sourceIn(), fps)

        framelist = '%s-%s' % (int(item.sourceIn()), int(item.sourceOut()))

        # create output path
        output_path = utils.get_path(instance, 'dpx', self.log)
        output_path = output_path.replace('%04d', '####')
        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))

        # adding deadline data
        job_data = {'Group': 'draft','Pool': 'medium', 'Plugin': 'Draft',
                    'LimitGroups': 'draft', 'ChunkSize': 5,
                    'Frames': framelist, 'OutputFilename0': output_path}

        plugin_data = {}

        script = os.path.dirname(draft.__file__)
        script = os.path.join(script, 'exr_to_dpx_cineon.py')
        plugin_data['scriptFile'] = script
        plugin_data['ScriptArg0'] = 'frameList=%s' % framelist
        plugin_data['ScriptArg1'] = 'outFile=%s\n' % output_path
        plugin_data['ScriptArg2'] = 'inFile=%s\n' % input_path

        data = {'job': job_data, 'plugin': plugin_data}
        instance.set_data('deadlineData', value=data)
