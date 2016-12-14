import pymel
import pyblish.api


class BumpyboxMayaValidateSceneModified(pyblish.api.ContextPlugin):
    """ Validates whether the scene has been saved since modifying. """

    order = pyblish.api.ValidatorOrder - 0.49
    hosts = ["maya"]
    label = "Scene Modified"
    optional = True

    def process(self, context):

        if pymel.core.dgmodified():
            self.log.info("Scene modified. Saving scene...")
            pymel.core.saveFile()
