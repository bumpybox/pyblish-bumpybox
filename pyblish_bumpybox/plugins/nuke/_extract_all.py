import os
import tempfile

import pyblish.api

import nuke

@pyblish.api.log
class ExtractAll(pyblish.api.Extractor):
    """
    """

    families = ['all']
    hosts = ['nuke']
    version = (0, 1, 0)

    def process_instance(self, instance):
        """
        """
        filename = os.path.basename(instance.context.data('current_file'))
        filename = os.path.splitext(filename)[0]
        filename = filename + ".nk"

        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(
            temp_dir, filename)

        self.log.info("Extracting {0} locally..".format(instance))

        instance.set_data('filename', value=filename)
        nuke.scriptSaveAs(temp_file)

        self.commit(path=temp_dir, instance=instance)

        self.log.info("Extraction successful.")
