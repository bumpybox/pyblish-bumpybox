import pymel
import pyblish.api


class BumpyboxMayaRepairSceneModified(pyblish.api.Action):

    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):

        pymel.core.saveFile()


class BumpyboxMayaValidateSceneModified(pyblish.api.ContextPlugin):
    """ Validates whether the scene has been saved since modifying. """

    order = pyblish.api.ValidatorOrder
    hosts = ["maya"]
    label = "Scene Modified"
    optional = True
    actions = [BumpyboxMayaRepairSceneModified]

    def process(self, context):

        msg = "Scene has not been saved since modifying."
        assert not pymel.core.dgmodified(), msg
