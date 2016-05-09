import pymel.core
import maya.cmds as cmds

import pyblish.api
import pyblish_qml
from pyblish_bumpybox.environment_variables import utils


# Pyblish callbacks for presisting instance states to the scene
def toggle_instance(instance, new_value, old_value):

    if instance.data['family'] == 'deadline.render':
        pymel.core.PyNode(instance).renderable.set(bool(new_value))

    if instance.data['family'] == 'alembic.asset':
        pymel.core.PyNode(instance).pyblish_alembic.set(bool(new_value))

pyblish.api.register_callback("instanceToggled", toggle_instance)


# setting Pyblish window title to ftrack context path
def setPyblishWindowTitle():

    pyblish_qml.settings.WindowTitle = utils.getFtrackContextPath()

cmds.evalDeferred('setPyblishWindowTitle()')
