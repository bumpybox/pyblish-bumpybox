import pymel.core
import pyblish.api


class ValidateMayaRenderCamera(pyblish.api.Validator):
    """ Validates render camera """

    families = ["renderlayer"]
    optional = True
    label = "Render Camera"

    def process(self, instance):

        # Validate non native camera active
        render_cameras = instance.data["cameras"]

        for c in pymel.core.ls(type="camera"):
            if c.renderable.get():
                render_cameras.append(c)

        render_cameras = list(set(render_cameras))

        msg = "No renderable camera selected."
        assert render_cameras, msg

        msg = "Can't render multiple cameras. "
        msg += "Please use a render layer instead"
        assert len(render_cameras) == 1, msg
