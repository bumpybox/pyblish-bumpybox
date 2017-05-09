import pymel
import pyblish.api


class BumpyboxMayaRepairVraySettings(pyblish.api.Action):

    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):

        settings = pymel.core.PyNode("vraySettings")

        # Repairing file name prefix
        settings.fileNamePrefix.set("<Layer>/<Scene>")

        # Repairing animation
        settings.animType.set(1)

        # Repairing name padding
        settings.fileNamePadding.set(4)


class BumpyboxMayaValidateVraySettings(pyblish.api.InstancePlugin):
    """ Validates render layer settings. """

    order = pyblish.api.ValidatorOrder
    optional = True
    families = ["vray"]
    label = "Vray Settings"
    actions = [BumpyboxMayaRepairVraySettings]
    hosts = ["maya"]

    def process(self, instance):

        settings = pymel.core.PyNode("vraySettings")

        # File name prefix
        current = settings.fileNamePrefix.get()
        expected = "<Layer>/<Scene>"

        msg = "File name prefix is incorrect. Current: \"{0}\"."
        msg += " Expected: \"{1}\""
        assert expected == current, msg.format(current, expected)

        # Enable animation
        msg = "Expecting Animation to be \"Standard\""
        assert settings.animType.get() == 1, msg

        # Frame name padding
        msg = "Expecting Frame name padding to be \"4\""
        assert settings.fileNamePadding.get() == 4, msg
