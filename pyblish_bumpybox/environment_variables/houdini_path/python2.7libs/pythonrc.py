import pyblish.api


# Pyblish callbacks for presisting instance states to the scene
def toggle_instance(instance, new_value, old_value):

    # all instances are nodes, except for the scene instance
    try:
        instance[0].bypass(not bool(new_value))
    except:
        pass

pyblish.api.register_callback("instanceToggled", toggle_instance)

# register gui
pyblish.api.register_gui("pyblish_lite")
