from pyblish import api
from pyblish_bumpybox import inventory


class ValidateDatatype(api.InstancePlugin):
    """Validate output datatype matches with input."""

    order = inventory.get_order(__file__, "ValidateDatatype")
    families = ["write"]
    label = "Datatype"
    optional = True
    targets = ["default", "process"]

    def process(self, instance):

        # Only validate these channels
        channels = [
            "N_Object",
            "N_World",
            "P_Object",
            "P_World",
            "Pref",
            "UV",
            "velocity",
            "cryptomatte"
        ]

        valid_channels = []
        for node_channel in instance[0].channels():
            for channel in channels:
                if node_channel.startswith(channel):
                    valid_channels.append(node_channel)

        if valid_channels:
            msg = (
                "There are 32-bit channels: {0}.\n\nConsider changing the"
                " output to 32-bit to preserve data.".format(valid_channels)
            )
            assert instance[0]["datatype"].value().startswith("32"), msg
