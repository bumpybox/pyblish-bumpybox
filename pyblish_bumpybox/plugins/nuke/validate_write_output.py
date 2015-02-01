import pyblish.api

class ValidateWriteOutput(pyblish.api.Validator):
    """
    """

    families = ['Write Nodes']
    hosts = ['nuke']
    version = (0, 1, 0)

    def process_instance(self, instance):
        """
        """
        print instance
