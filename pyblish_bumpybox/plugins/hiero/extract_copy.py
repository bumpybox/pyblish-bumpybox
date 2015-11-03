import os

import pyblish.api
import hiero
from pyblish_bumpybox.plugins.hiero import utils


class ExtractCopy(pyblish.api.Extractor):
    """
    """

    families = ['copy.trackItem']
    label = 'Copy'

    def process(self, instance, context):

        item = instance[0]

        # create output path
        input_path = item.source().mediaSource().fileinfos()[0].filename()
        path = utils.get_path(instance, 'png', self.log)
        output_path = os.path.join(os.path.dirname(path),
                                                os.path.basename(input_path))

        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))

        # adding deadline data
        job_data = {'Group': 'ffmpeg','Pool': 'medium', 'Plugin': 'FFmpeg',
                    'OutputFilename0': output_path, 'Frames': 0}

        plugin_data = {'InputArgs0': '', 'OutputFile': output_path,
                            'ReplacePadding': False, 'UseSameInputArgs': False}

        plugin_data['OutputArgs'] = '-codec copy'
        plugin_data['InputFile0'] = input_path

        data = {'job': job_data, 'plugin': plugin_data}
        instance.set_data('deadlineData', value=data)
