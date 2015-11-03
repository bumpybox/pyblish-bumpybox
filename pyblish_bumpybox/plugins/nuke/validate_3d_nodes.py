import nuke
import pyblish.api


class Validate3dNodes(pyblish.api.Validator):
    """
    """

    families = ['axis', 'camera']
    label = '3D Nodes'

    def process(self, instance):

        node = instance[0]

        msg = '%s has "read from file" enabled.' % node.name()
        assert not bool(node['read_from_file_link'].getValue()), msg

    def repair(self, instance):

        node = instance[0]

        node['read_from_file_link'].setValue(False)
