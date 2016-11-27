import pyblish.api
from pyblish_bumpybox.plugins.maya import utils
reload(utils)


class RepairComponentShading(pyblish.api.Action):

    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context):
        utils.hfFixBadShading()


class ValidateComponentShading(pyblish.api.Validator):
    """"""

    families = ['scene']
    optional = True
    label = 'Component Shading'
    actions = [RepairComponentShading]

    def process(self, instance):

        msg = 'Found objects with component shading.'
        assert utils.hfCheckShading(self.log), msg
