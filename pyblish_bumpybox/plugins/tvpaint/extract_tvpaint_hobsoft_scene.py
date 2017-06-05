import os
import shutil

import pyblish.api


class ExtractTVPaintHobsoftScene(pyblish.api.Extractor):
    """ Extract work file to Hobsoft drive
    """

    families = ['scene']
    label = 'Hobsoft Sync'

    def process(self, instance, context):

        current_file = instance.data('workPath')
        ftrack_data = context.data('ftrackData')

        if ftrack_data['Project']['name'] != 'ethel_and_ernest':
            return

        sequence_name = ftrack_data['Sequence']['name']
        shot_name = 'c' + ftrack_data['Shot']['name'].split('c')[1]
        filename = ftrack_data['Shot']['name'] + '_ee.tvpp'

        publish_file = os.path.join('B:\\', 'film', sequence_name, shot_name,
                                                        'tvpaint', filename)

        # create publish directory
        if not os.path.exists(os.path.dirname(publish_file)):
            os.makedirs(os.path.dirname(publish_file))

        # copy work file to publish
        shutil.copy(current_file, publish_file)
