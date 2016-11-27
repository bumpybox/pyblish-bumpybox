import pyblish.api


class ValidateRenderer(pyblish.api.Validator):
    """ Validates settings """

    families = ['deadline.render']
    optional = True
    label = 'Renderer'

    def process(self, instance):

        # validate renderer
        msg = "Render Farm can't handle hardware "
        msg += "renders on: %s" % instance.data["name"]
        renderer = instance.data('deadlineData')['plugin']['Renderer']
        assert 'hardware' not in renderer.lower(), msg
