import pymel.core as pc

from Qt import QtWidgets
from pyblish_bumpybox.tools import processing_location


def application_function(selection, localProcessing):

    # Look for any sets starting with remote
    remote_set = None
    for object_set in pc.ls(type="objectSet"):
        if object_set.name().startswith("remote"):
            remote_set = object_set

    # Create remote set is none is present
    if not remote_set:
        remote_set = pc.sets()

    # Add\Remove from remote set
    for item in selection:
        if localProcessing:
            remote_set.remove(pc.PyNode(item))
        else:
            remote_set.add(pc.PyNode(item))


def show():

    # Find Maya Window and instantiate tool window as child
    parent = next(
        o for o in QtWidgets.QApplication.instance().topLevelWidgets()
        if o.objectName() == "MayaWindow"
    )

    win = processing_location.Window(parent)

    # Collect sets named starting with "remote".
    remote_members = []
    for object_set in pc.ls(type="objectSet"):
        if object_set.name().startswith("remote"):
            remote_members.extend(object_set.members())

    for layer in pc.ls(type="renderLayer"):
        # Skipping defaultRenderLayers
        if layer.name().endswith("defaultRenderLayer"):
            continue

        # Add all renderlayers
        if layer in remote_members:
            win.add_item(layer.name(), remote=True)
        else:
            win.add_item(layer.name())

    # Override default application function
    win.application_function = application_function

    win.show()
