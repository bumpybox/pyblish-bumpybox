import imp

import pyblish.api


# Pyblish callbacks for presisting instance states to the scene
def custom_toggle_instance(instance, new_value, old_value):

    # All instances are nodes, except for the scene instance
    try:
        instance[0]["disable"].setValue(not bool(new_value))
    except:
        pass


pyblish.api.register_callback("instanceToggled", custom_toggle_instance)

# register pyblish_qml
pyblish.api.register_gui("pyblish_lite")

# Adding ftrack assets if import is available.
try:
    imp.find_module("ftrack_connect")
    imp.find_module("ftrack_connect_nuke")

    import ftrack_assets
    ftrack_assets.register_assets()
    import ftrack_init
    ftrack_init.init()
except ImportError as error:
    print "Could not find ftrack modules: " + str(error)
