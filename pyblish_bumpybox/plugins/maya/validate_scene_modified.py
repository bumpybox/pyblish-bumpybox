from pyblish import api
from pyblish_bumpybox import inventory


class ValidateSceneModified(api.ContextPlugin):
    """ Validates whether the scene has been saved since modifying. """

    order = inventory.get_order(__file__, "ValidateSceneModified")
    hosts = ["maya"]
    label = "Scene Modified"
    optional = True

    def process(self, context):
        import pymel.core
        import maya.cmds as cmds

        # Using "pymel.core.dgmodified()" seems to crash in 2017,
        # when using the time Editor.
        if (cmds.file(query=True, modified=True) and
           pymel.core.system.sceneName()):
            self.log.info("Scene modified. Saving scene...")
            pymel.core.saveFile()
