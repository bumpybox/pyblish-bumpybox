import imp

import maya.cmds as cmds

import pyblish.api
import pyblish_lite


# Disabling debug logging, cause of FTrack constant stream of print outs.
def disableDebug():
    import logging
    logging.getLogger().setLevel(logging.INFO)


cmds.evalDeferred('disableDebug()', lowestPriority=True)


# Pyblish callbacks for presisting instance states to the scene.
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

    if "playblast" in instance.data.get("families", []):

        node.getTransform().publish.set(new_value)


pyblish.api.register_callback("instanceToggled", toggle_instance)

# Register pyblish_lite.
pyblish.api.register_gui("pyblish_lite")

# pyblish_lite settings
pyblish_lite.settings.InitialTab = "overview"

# Adding ftrack assets if import is available.
try:
    imp.find_module("ftrack_connect")
    imp.find_module("ftrack_connect_maya")

    import ftrack_assets
    import ftrack_init
    ftrack_assets.register_assets()
    ftrack_init.init()
except ImportError as error:
    print "Could not find ftrack modules: " + str(error)
