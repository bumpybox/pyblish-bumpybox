import pymel.core
import maya.cmds as cmds

import pyblish.api


class ValidateMayaSceneModified(pyblish.api.ContextPlugin):
    """ Validates whether the scene has been saved since modifying. """

    order = pyblish.api.ExtractorOrder - 0.49
    hosts = ["maya"]
    label = "Scene Modified"
    optional = True

    def process(self, context):

        # Using "pymel.core.dgmodified()" seems to crash in 2017,
        # when using the time Editor.
        if (cmds.file(query=True, modified=True) and
           pymel.core.system.sceneName()):
            self.log.info("Scene modified. Saving scene...")
            pymel.core.saveFile()
