import nuke
import nukescripts.autobackdrop as na

from Qt import QtGui
from pyblish_bumpybox.tools import processing_location


def application_function(selection, localProcessing):

    for item in selection:
        node = nuke.toNode(item)

        if localProcessing:
            for backdrop in nuke.allNodes():
                if backdrop.Class() == "BackdropNode":
                    if backdrop.name().startswith("remote"):
                        if na.nodeIsInside(node, backdrop):
                            nuke.delete(backdrop)
        else:
            node["selected"].setValue(True)
            backdrop = na.autoBackdrop()
            backdrop["name"].setValue("remote_" + node.name())


def show():

    main_window = QtGui.QApplication.activeWindow()
    win = processing_location.Window(main_window)

    # Get remote nodes
    remote_nodes = []
    for node in nuke.allNodes():
        if node.Class() == "BackdropNode":
            if node.name().startswith("remote"):
                remote_nodes.extend(node.getNodes())

    remote_nodes = list(set(remote_nodes))

    # creating instances per write node
    for node in nuke.allNodes():
        if node.Class() != "Write":
            continue

        if node in remote_nodes:
            win.add_item(node.name(), remote=True)
        else:
            win.add_item(node.name())

    win.application_function = application_function

    win.show()
