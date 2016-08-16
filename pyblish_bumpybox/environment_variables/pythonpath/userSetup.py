import pymel.core
import maya.cmds as cmds

import pyblish.api


# disabling debug logging, cause of FTrack constant stream of print outs
def disableDebug():
    import logging
    logging.getLogger().setLevel(logging.INFO)

cmds.evalDeferred('disableDebug()', lowestPriority=True)


# Pyblish callbacks for presisting instance states to the scene
def toggle_instance(instance, new_value, old_value):

    if instance.data["family"] == "deadline.render":
        pymel.core.PyNode(instance).renderable.set(bool(new_value))

    if instance.data["family"] == "alembic.asset":
        pymel.core.PyNode(instance).pyblish_alembic.set(bool(new_value))

    if instance.data["family"] == "alembic.camera":
        attr = "pyblish_camera"
        node = instance[0]

        if pymel.core.attributeQuery(attr, node=node.name(), exists=True):
            node.attr(attr).set(new_value)
        else:
            pymel.core.addAttr(node, longName=attr, defaultValue=new_value,
                               attributeType="bool")

    if instance.data["family"] == "texture":
        attr = "pyblish_texture"
        node = instance[0]

        if pymel.core.attributeQuery(attr, node=node.name(), exists=True):
            node.attr(attr).set(new_value)
        else:
            pymel.core.addAttr(node, longName=attr, defaultValue=new_value,
                               attributeType="bool")
    """
    if "families" in instance.data and "cache.*" in instance.data["families"]:

        attr = instance.data["family"].replace(".", "_")
        node = instance.data["set"]

        if pymel.core.attributeQuery(attr, node=node.name(), exists=True):
            node.attr(attr).set(new_value)
        else:
            pymel.core.addAttr(node, longName=attr, defaultValue=new_value,
                               attributeType="bool")
   """

pyblish.api.register_callback("instanceToggled", toggle_instance)

# register pyblish_qml
pyblish.api.register_gui("pyblish_lite")
