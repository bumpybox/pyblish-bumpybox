import maya.cmds as cmds

import pyblish.api


# disabling debug logging, cause of FTrack constant stream of print outs
def disableDebug():
    import logging
    logging.getLogger().setLevel(logging.INFO)


cmds.evalDeferred('disableDebug()', lowestPriority=True)


# Pyblish callbacks for presisting instance states to the scene
def toggle_instance(instance, new_value, old_value):

    node = instance[0]

    families = instance.data.get("families", [])
    if "cache" in families or "scene" in families:
        attrs = []
        for attr in node.listAttr(userDefined=True):
            attrs.append(attr.name(includeNode=False))

        attr_list = list(set(attrs) & set(families))

        if attr_list:
            node.attr(attr_list[0]).set(new_value)

    if "renderlayer" in instance.data.get("families", []):

        node.renderable.set(new_value)


pyblish.api.register_callback("instanceToggled", toggle_instance)

# register pyblish_qml
pyblish.api.register_gui("pyblish_lite")
