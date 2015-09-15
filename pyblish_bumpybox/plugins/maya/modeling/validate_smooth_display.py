import pyblish.api
import pymel


class ValidateSmoothDisplay(pyblish.api.Validator):
    """ Ensures a flat hierarchy """

    families = ['geometry']
    optional = True
    label = 'Modeling - Smooth Display'

    def process(self, instance):

        node = instance[0]

        msg = '%s has smooth display enabled' % node.name()
        assert not node.displaySmoothMesh.get(), msg

    def repair(self, instance):

         node = instance[0]
         node.displaySmoothMesh.set(False)
