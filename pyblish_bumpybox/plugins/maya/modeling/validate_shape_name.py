from pyblish import api
from pyblish_bumpybox import inventory


class RepairShapeName(api.Action):
    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):
        import pymel.core

        invalid_shapes = []
        for shp in pymel.core.ls(type="mesh"):
            if "|" in shp.name():
                invalid_shapes.append(shp)

        for shp in invalid_shapes:
            pymel.core.rename(shp, shp.getParent().name() + "Shape")


class ValidateShapeName(api.ContextPlugin):
    """ No two shapes can have the same name. """

    order = inventory.get_order(__file__, "ValidateShapeName")
    label = "Shape Name"
    actions = [RepairShapeName]
    optional = True

    def process(self, context):
        import pymel.core

        validate = False
        valid_families = set(["mayaAscii", "mayaBinary", "alembic"])
        for instance in context:
            if set(instance.data["families"]) & valid_families:
                if instance.data.get("publish", True):
                    validate = True

        if not validate:
            return

        invalid_shapes = []
        msg = "Duplicate shape names:"
        for shp in pymel.core.ls(type="mesh"):
            if "|" in shp.name():
                invalid_shapes.append(shp)
                msg += "\n\n" + shp.name()

        assert not invalid_shapes, msg
