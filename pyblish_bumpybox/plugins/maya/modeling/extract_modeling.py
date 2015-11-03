import pymel
import pyblish.api

class PassthroughModeling(pyblish.api.Validator):

    families = ['geometry', 'scene', 'reference.geometry']
    label = 'Passthrough'
    ExtractModeling = True

    def process(self, instance):

        pass

class ExtractModeling(pyblish.api.Integrator):
    """ Extract work file to 'publish' directory next to work file
    """

    families = ['geometry']
    label = 'Modeling'

    def process(self, context):

        nodes = []
        publish_file = ''

        for item in context.data('results'):
            try:
                item['plugin'].ExtractModeling
                instance = item['instance']
                if instance.data('family') == 'geometry':
                    nodes.extend(instance)
                if instance.data('family') == 'reference.geometry':
                    nodes.extend(instance)
                if instance.data('family') == 'scene':
                    publish_file = instance.data('publishPath')
            except:
                pass

        pymel.core.select(nodes)
        pymel.core.system.exportSelected(publish_file,
        constructionHistory=False, preserveReferences=True, shader=True,
        constraints=False, force=True)
