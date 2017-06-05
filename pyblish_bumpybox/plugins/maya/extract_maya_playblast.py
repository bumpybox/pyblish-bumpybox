import pyblish.api
from capture import capture


class ExtractMayaPlayblast(pyblish.api.InstancePlugin):
    """ Extracts playblast. """

    order = pyblish.api.ExtractorOrder
    families = ["playblast"]
    optional = True
    label = "Playblast"
    hosts = ["maya"]

    def process(self, instance):

        filename = list(instance.data["collection"])[0]
        filename = filename.replace(
            instance.data["collection"].format("{tail}"),
            ""
        )
        capture(
            instance[0].getTransform().name(),
            filename=filename,
            viewer=False,
            show_ornaments=False,
            overwrite=True,
            off_screen=True,
            viewport_options={"rendererName": "vp2Renderer"},
            viewport2_options={
                "multiSampleEnable": True, "multiSampleCount": 8
            },
            camera_options={"panZoomEnabled": False},
        )
