import pyblish.api
import pymel


class CollectMesh(pyblish.api.Collector):
    """
    """

    def process(self, context):

        transforms = []
        for node in pymel.core.ls(type='mesh'):
            transforms.append(node.getParent())

        for node in set(transforms):
            instance = context.create_instance(name=node.name())
            instance.set_data('family', value='geometry')
            instance.add(node)
