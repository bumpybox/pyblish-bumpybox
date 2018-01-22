import pyblish.api


class RepairMayaModelingShapeName(pyblish.api.Action):
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


class ValidateMayaModelingShapeName(pyblish.api.ContextPlugin):
    """ No two shapes can have the same name. """

    order = pyblish.api.ValidatorOrder
    label = "Shape Name"
    actions = [RepairMayaModelingShapeName]
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
