import os

import pyblish.api
import hiero
from pyblish_bumpybox.plugins.hiero import utils
reload(utils)


class ExtractAudio(pyblish.api.Extractor):
    """ Extracting audio
    """

    families = ['h264.trackItem', 'prores.trackItem']
    label = 'Audio'
    order = pyblish.api.Extractor.order - 0.5

    def process(self, instance):

        item = instance[0]

        # create output path
        output_path = utils.get_path(instance, 'wav', self.log, sequence=False)
        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))

        item.sequence().writeAudioToFile(output_path, item.timelineIn(),
                                        item.timelineOut())

        instance.set_data('audio', value=output_path)
