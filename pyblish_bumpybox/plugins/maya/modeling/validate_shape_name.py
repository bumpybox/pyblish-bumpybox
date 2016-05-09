import pyblish.api

import pymel.core


class RepairShapeName(pyblish.api.Action):
    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):

        invalid_shapes = []
        for shp in pymel.core.ls(type='mesh'):
            if '|' in shp.name():
                invalid_shapes.append(shp)

        for shp in invalid_shapes:
            pymel.core.rename(shp, shp.getParent().name() + 'Shape')


class ValidateShapeName(pyblish.api.ContextPlugin):
    """ No two shapes can have the same name. """
    order = pyblish.api.ValidatorOrder
    label = 'Shape Name'
    actions = [RepairShapeName]

    def process(self, context):

        invalid_shapes = []
        msg = 'Duplicate shape names:'
        for shp in pymel.core.ls(type='mesh'):
            if '|' in shp.name():
                invalid_shapes.append(shp)
                msg += '\n\n' + shp.name()

        assert not invalid_shapes, msg
