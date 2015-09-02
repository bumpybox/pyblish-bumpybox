import pyblish.api


class ValidateSceneVersion(pyblish.api.Validator):
    """Validates the existence of version number on the scene
    """

    families = ['scene']
    label = 'Scene Version'

    def process(self, context):

        msg = 'Could not find a version number in the scene name.'
        assert context.has_data('version'), msg
