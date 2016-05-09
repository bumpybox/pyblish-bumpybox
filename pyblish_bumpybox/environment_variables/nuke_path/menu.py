import pyblish.api
import pyblish_qml
from pyblish_bumpybox.environment_variables import utils


# Pyblish callbacks for presisting instance states to the scene
def custom_toggle_instance(instance, new_value, old_value):

    if instance.data['family'] == 'deadline.render':
        instance[0]['disable'].setValue(not bool(new_value))

pyblish.api.register_callback("instanceToggled", custom_toggle_instance)

# setting Pyblish window title to ftrack context path
pyblish_qml.settings.WindowTitle = utils.getFtrackContextPath()
