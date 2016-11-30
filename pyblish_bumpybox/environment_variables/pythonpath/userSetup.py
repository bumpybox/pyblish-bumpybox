import maya.cmds as cmds

import pyblish.api


# disabling debug logging, cause of FTrack constant stream of print outs
def disableDebug():
    import logging
    logging.getLogger().setLevel(logging.INFO)


cmds.evalDeferred('disableDebug()', lowestPriority=True)


# Pyblish callbacks for presisting instance states to the scene
def toggle_instance(instance, new_value, old_value):

    if "cache" in instance.data["families"]:
        attrs = []
        for attr in instance[0].listAttr(userDefined=True):
            attrs.append(attr.name(includeNode=False))

        attr_list = list(set(attrs) & set(instance.data["families"]))

        if attr_list:
            instance[0].attr(attr_list[0]).set(new_value)


#pyblish.api.register_callback("instanceToggled", toggle_instance)

# register pyblish_qml
pyblish.api.register_gui("pyblish_lite")
