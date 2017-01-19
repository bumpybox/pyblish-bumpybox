import pyblish.api
from capture import capture


class BumpyboxMayaExtractPlayblast(pyblish.api.InstancePlugin):
    """ Extracts playblast. """

    order = pyblish.api.ExtractorOrder
    families = ["playblast"]
    optional = True
    label = "Playblast"
    hosts = ["maya"]

    def process(self, instance):

        capture(
            instance[0].getTransform().name(),
            filename=list(instance.data["collection"])[0],
            viewer=False,
            show_ornaments=False,
            overwrite=True,
            off_screen=True
        )
