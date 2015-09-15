import pyblish.api
import pymel


class CollectReferences(pyblish.api.Collector):
    """
    """

    def process(self, context):

        for node in pymel.core.ls(type='reference'):
            if 'sharedReferenceNode' in node.name():
                continue

            if node.isReferenced():
                continue

            file_ref = pymel.core.system.FileReference(node)
            try:
                self.log.info(file_ref.path)
            except:
                continue

            if not file_ref.isLoaded():
                continue

            instance = context.create_instance(name=node.name())
            instance.set_data('family', value='reference')
            instance.add(node)
