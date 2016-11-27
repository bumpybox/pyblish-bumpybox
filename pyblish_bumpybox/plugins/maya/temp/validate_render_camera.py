import pymel.core
import pyblish.api


class ValidateRenderCamera(pyblish.api.Validator):
    """ Validates settings """

    families = ['deadline.render']
    optional = True
    label = 'Render Camera'

    def process(self, instance):

        # validate non native camera active
        render_cameras = instance.data['data']['cameras']

        for c in pymel.core.ls(type='camera'):
            if c.renderable.get():
                render_cameras.append(c)

        render_cameras = list(set(render_cameras))

        msg = 'No renderable camera selected.'
        assert render_cameras, msg

        check = True
        for c in render_cameras:
            if c.getParent().name() in ['persp', 'top', 'side', 'front']:
                check = False

        msg = 'Renderable Cameras is incorrect. Expected non default camera.'
        assert check, msg

        msg = "Can't render multiple cameras. "
        msg += "Please use a render layer instead"
        assert len(render_cameras) == 1, msg

        msg = "No renderable camera seleted."
        assert render_cameras, msg
