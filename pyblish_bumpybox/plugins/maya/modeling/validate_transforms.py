import pymel
import pyblish.api


@pyblish.api.log
class ValidateTransforms(pyblish.api.Validator):
    """"""

    families = ['scene']

    def process(self, instance):

        check = True
        for node in pymel.core.ls(type='mesh'):
            transform = node.getParent()

            if sum(transform.getRotatePivot(space='world')):
                msg = '"%s" pivot is not at world zero.' % node.name()
                self.log.error(msg)
                check = False

            if sum(transform.getRotation(space='world')):
                msg = '"%s" pivot axis is not aligned to world.' % node.name()
                self.log.error(msg)
                check = False

        msg = "Transforms in the scene aren't reset."
        msg += ' Please reset by moving the pivot to world zero, and freeze the transform.'
        assert check, msg
