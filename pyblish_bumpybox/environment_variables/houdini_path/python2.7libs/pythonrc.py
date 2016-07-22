import pyblish.api
import pyblish_qml
from pyblish_bumpybox.environment_variables import utils


# Pyblish callbacks for presisting instance states to the scene
def toggle_instance(instance, new_value, old_value):

    # all instances are nodes, except for the scene instance
    try:
        instance[0].bypass(not bool(new_value))
    except:
        pass

pyblish.api.register_callback("instanceToggled", toggle_instance)


# setting Pyblish window title to ftrack context path
def setPyblishWindowTitle():

    pyblish_qml.settings.WindowTitle = utils.getFtrackContextPath()

setPyblishWindowTitle()
