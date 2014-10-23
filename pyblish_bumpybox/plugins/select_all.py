import pyblish.api

@pyblish.api.log
class SelectAll(pyblish.api.Selector):
    """
    """

    hosts = ['maya', 'modo']
    version = (0, 1, 0)

    def process_context(self, context):
        """
        """

        instance = context.create_instance(name='all')
        
        instance.set_data('family', value='all')
