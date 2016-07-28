import os

import pymel
import pyblish.api


class ExtractSceneSave(pyblish.api.Extractor):
    """ Extracts the scene in ma format """

    order = pyblish.api.Extractor.order - 0.1
    families = ["scene.ma"]
    label = "Scene .ma"
    optional = True

    def process(self, instance):

        file_path = instance.context.data["currentFile"].replace(".mb", ".ma")
        basename = os.path.basename(file_path)
        dirname = os.path.dirname(file_path)
        file_path = os.path.join(dirname, "publish", basename)

        pymel.core.system.exportAll(file_path, force=True, type="mayaAscii",
                                    preserveReferences=True)
