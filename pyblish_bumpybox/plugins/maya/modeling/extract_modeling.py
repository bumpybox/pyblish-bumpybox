import pymel.core
import pyblish.api


class ExtractModeling(pyblish.api.Extractor):
    """ Extracts instances of 'geometry' and 'reference.geometry' family """

    families = ['geometry']
    label = 'Modeling'

    def process(self, context):

        nodes = []
        publish_file = ''

        for instance in context:

            if not instance.data.get("publish", True):
                continue

            if instance.data('family') == 'geometry':
                nodes.extend(instance)
            if instance.data('family') == 'reference.geometry':
                nodes.extend(instance)
            if instance.data('family') == 'scene':
                publish_file = instance.data('publishPath')

        pymel.core.select(nodes)
        pymel.core.system.exportSelected(publish_file,
                                         constructionHistory=False,
                                         preserveReferences=True, shader=True,
                                         constraints=False, force=True)
