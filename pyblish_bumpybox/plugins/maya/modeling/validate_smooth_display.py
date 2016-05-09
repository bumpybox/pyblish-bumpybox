import pyblish.api


class ValidateSmoothDisplay(pyblish.api.Validator):
    """ Ensures a flat hierarchy """

    families = ['geometry']
    optional = True
    label = 'Smooth Display'

    def process(self, instance):

        check = True
        for node in instance:
            if node.displaySmoothMesh.get():
                msg = '%s has smooth display enabled' % node.name()
                self.log.error(msg)
                check = False

        assert check, 'Smooth display enabled meshes in the scene.'

    def repair(self, instance):

        for node in instance:
            node.displaySmoothMesh.set(False)
