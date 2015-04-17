import pyblish.api


@pyblish.api.log
class ValidateWriteNodesAmount(pyblish.api.Validator):
    """Validates that the output directory for the write nodes exists"""

    families = ['writeNode']
    hosts = ['nuke']
    version = (0, 1, 0)

    def process_context(self, context):
        if len(context) != 1:
            msg = 'There are more than 1 write node active in the script.'

            raise ValueError(msg)
