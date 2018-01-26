from pyblish import api
from pyblish_bumpybox import inventory


class ValidateRenderCamera(api.InstancePlugin):
    """ Validates render camera """

    order = inventory.get_order(__file__, "ValidateRenderCamera")
    families = ["renderlayer"]
    optional = True
    label = "Render Camera"

    def process(self, instance):
        import pymel.core
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
