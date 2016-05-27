import shutil

import pyblish.api
import pipeline_schema


class IntegrateCleanUp(pyblish.api.ContextPlugin):
    """ Cleans up any temporary files from publishing """

    label = 'Clean Up'
    order = pyblish.api.IntegratorOrder + 0.4
    optional = True

    def process(self, context):

        data = pipeline_schema.get_data()
        data['extension'] = 'temp'
        output_dir = pipeline_schema.get_path('temp_dir', data=data)
        shutil.rmtree(output_dir, ignore_errors=True)
