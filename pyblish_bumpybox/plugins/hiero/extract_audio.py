import os

import pyblish.api
import pipeline_schema


class ExtractAudio(pyblish.api.InstancePlugin):
    """ Extracting audio """

    families = ['trackItem']
    label = 'Audio'
    order = pyblish.api.Extractor.order - 0.5

    def process(self, instance):

        item = instance[0]
        data = pipeline_schema.get_data()
        data['extension'] = 'wav'
        output_file = pipeline_schema.get_path('temp_file', data=data)

        output_dir = os.path.dirname(output_file)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        item.sequence().writeAudioToFile(output_file, item.timelineIn(),
                                         item.timelineOut())

        instance.set_data('audio', value=output_file)
