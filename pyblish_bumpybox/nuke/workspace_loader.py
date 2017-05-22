import nuke

from Qt import QtGui
from pyblish_bumpybox.tools import workspace_loader


def import_img(instance):

    # Create read node
    node = nuke.createNode("Read", inpanel=False)

    # Set file path
    file_path = instance.data["collection"].format("{head}{padding}{tail}")
    node["file"].setValue(file_path)

    # Set range
    collection_range = instance.data["collection"].format("{range}")
    start = int(collection_range.split("-")[0])
    end = int(collection_range.split("-")[1])
    node["first"].setValue(start)
    node["origfirst"].setValue(start)
    node["last"].setValue(end)
    node["origlast"].setValue(end)


def application_function(instance):

    if "img" in instance.data["families"]:
        import_img(instance)
        return

    raise ValueError("Instance not supported.")


def show():

    main_window = QtGui.QApplication.activeWindow()
    win = workspace_loader.Window(main_window)

    win.application_function = application_function

    win.show()
