import os
import shutil

import pyblish.api


@pyblish.api.log
class ExtractScene(pyblish.api.Extractor):
    """ Extract work file to 'publish' directory next to work file
    """

    families = ['scene']
    hosts = ['*']
    version = (0, 1, 0)
    label = 'Scene'

    def process(self, instance):

        current_file = instance.data('workPath')
        publish_file = instance.data('publishPath')
        publish_dir = os.path.dirname(instance.data('publishPath'))

        # create publish directory
        if not os.path.exists(publish_dir):
            os.makedirs(publish_dir)

        # copy work file to publish
        shutil.copy(current_file, publish_file)
