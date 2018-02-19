from pyblish import api
from pyblish_bumpybox import inventory


class ValidateName(api.InstancePlugin):
    """Validates the name of the instance."""

    order = inventory.get_order(__file__, "ValidateName")
    families = [
        "playblast", "alembic", "mayaAscii", "mayaBinary", "camera", "geometry"
    ]
    optional = True
    label = "Name"
    targets = ["process.local"]

    def process(self, instance):

        msg = "Node name \"{0}\" is not unique.".format(instance.data["name"])
        assert "|" not in instance.data["name"], msg
