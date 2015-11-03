import pyblish.api
import pymel


class CollectMesh(pyblish.api.Collector):
    """
    """

    def process(self, context):

        transforms = []
        for node in pymel.core.ls(type='mesh'):
            transforms.append(node.getParent())

        ref_objs = []
        valid_objs = []
        invalid_objs = []
        for node in set(transforms):
            if node.isReferenced():
                ref_objs.append(node)
                continue
            if node.getParent():
                invalid_objs.append(node)
            else:
                valid_objs.append(node)

        if ref_objs:
            ref_instance = context.create_instance(name='reference meshes')
            ref_instance.set_data('family', value='reference.geometry')
            for obj in ref_objs:
                ref_instance.add(obj)

        if valid_objs:
            instance = context.create_instance(name='valid meshes')
            instance.set_data('family', value='geometry')
            for obj in valid_objs:
                instance.add(obj)

        if invalid_objs:
            instance = context.create_instance(name='invalid meshes')
            instance.set_data('family', value='geometry')
            for obj in invalid_objs:
                instance.add(obj)
