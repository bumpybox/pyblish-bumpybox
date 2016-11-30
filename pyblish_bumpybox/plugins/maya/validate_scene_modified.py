import pymel
import pyblish.api


class BumpyboxMayaRepairSceneModified(pyblish.api.Action):

    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):

        pymel.core.saveFile()


class BumpyboxMayaValidateSceneModified(pyblish.api.InstancePlugin):
    """ Validates whether the scene has been saved since modifying. """

    order = pyblish.api.ValidatorOrder
    families = ["scene"]
    hosts = ["maya"]
    label = "Scene Modified"
    optional = True
    actions = [BumpyboxMayaRepairSceneModified]

    def process(self, instance):

        msg = "Scene has not been saved since modifying."
        assert not pymel.core.dgmodified(), msg
