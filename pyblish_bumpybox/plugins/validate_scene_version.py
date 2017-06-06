import pyblish.api


class ValidateSceneVersion(pyblish.api.ContextPlugin):
    """ Validates the existence of version number on the scene. """

    order = pyblish.api.ValidatorOrder
    label = "Scene Version"

    def process(self, context):

        msg = "Could not find a version number in the scene name."
        assert context.has_data("version"), msg
