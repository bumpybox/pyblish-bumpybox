import pyblish.api


@pyblish.api.log
class ValidateSceneVersion(pyblish.api.Validator):
    """Validates the existence of version number on the scene
    """

    families = ['scene']
    label = 'Scene Version'

    def process(self, instance):

        msg = 'Could not find a version number in the scene name.'
        assert instance.context.has_data('version'), msg
