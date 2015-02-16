import os
import tempfile

import pyblish.api

from maya import cmds


@pyblish.api.log
class ExtractAll(pyblish.api.Extractor):
    """
    """

    families = ['all']
    hosts = ['maya']
    version = (0, 1, 0)

    def process_instance(self, instance):
        """
        """
        filename = os.path.basename(instance.context.data('current_file'))
        filename = os.path.splitext(filename)[0]
        filename = filename + ".mb"
        
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(
            temp_dir, filename)

        self.log.info("Extracting {0} locally..".format(instance))
        previous_selection = cmds.ls(selection=True)
        instance.set_data('filename', value=filename)
        cmds.file(temp_file, type='mayaBinary', exportAll=True)

        self.commit(path=temp_dir, instance=instance)

        if previous_selection:
            cmds.select(previous_selection, replace=True)
        else:
            cmds.select(deselect=True)

        self.log.info("Extraction successful.")
