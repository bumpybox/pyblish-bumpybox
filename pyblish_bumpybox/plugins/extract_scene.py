import os
import shutil

import pyblish.api


class ExtractScene(pyblish.api.InstancePlugin):
    """ Extract file to the "publishPath" datamember. """

    order = pyblish.api.ExtractorOrder
    families = ["scene"]
    label = "Scene"

    def process(self, instance):

        current_file = instance.data["path"]
        publish_file = instance.data["publishPath"]
        publish_dir = os.path.dirname(publish_file)

        # create publish directory
        if not os.path.exists(publish_dir):
            os.makedirs(publish_dir)

        # copy work file to publish
        shutil.copy(current_file, publish_file)
