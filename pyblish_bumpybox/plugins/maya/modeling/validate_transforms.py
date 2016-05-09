import pyblish.api


class ValidateTransforms(pyblish.api.Validator):
    """"""

    families = ['geometry']
    label = 'Transforms'

    def process(self, instance):

        check = True
        for node in instance:
            v = sum(node.getRotatePivot(space='world'))
            if v > 0.09:
                msg = '"%s" pivot is not at world zero.' % node.name()
                self.log.error(msg)
                check = False

            v = sum(node.getRotation(space='world'))
            if v != 0:
                msg = '"%s" pivot axis is not aligned to world.' % node.name()
                self.log.error(msg)
                check = False

            if sum(node.scale.get()) != 3:
                msg = '"%s" scale is not neutral.' % node.name()
                self.log.error(msg)
                check = False

        msg = "Transforms in the scene aren't reset."
        msg += ' Please reset by "Modify" > "Freeze Transformations",'
        msg += ' followed by "Modify" > "Reset Transformations".'
        assert check, msg
