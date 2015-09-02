import pymel
import pyblish.api


class Extractmodeling(pyblish.api.Extractor):
    """ Extract work file to 'publish' directory next to work file
    """

    order = pyblish.api.Extractor.order + 0.1
    families = ['scene']
    label = 'Modeling'

    def process(self, instance):

        transforms = []
        for m in pymel.core.ls(type='mesh'):
            transforms.append(m.getParent())

        pymel.core.select(set(transforms))

        publish_file = instance.data('publishPath')
        pymel.core.system.exportSelected(publish_file,
        constructionHistory=False, preserveReferences=True, shader=True,
        constraints=False, force=True)
