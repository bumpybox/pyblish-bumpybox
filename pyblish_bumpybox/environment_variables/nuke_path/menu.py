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
