import os

import nuke

import ftrack_api
from ftrack_connect_nuke.ui.legacy import scan_for_new_assets
import ftrack
from ftrack_connect.connector import HelpFunctions
from Qt import QtGui


def fpsInit():
    """
    Extecting a "fps" custom attribute on the parent entity of the task.

    Adds a "ftrackFPSSet" knob to the root node in Nuke,
    which indicates whether to set the FPS on startup.
    """

    node = nuke.root()

    # Adding/Checking ftrack fps attribute
    fps_set = False
    if "ftrackFPSSet" in node.knobs():
        fps_set = node["ftrackFPSSet"].getValue()
    else:
        node.addKnob(nuke.Tab_Knob("Ftrack"))
        knob = nuke.Boolean_Knob("ftrackFPSSet", "Set FPS on startup.")
        node.addKnob(knob)
        node["ftrackFPSSet"].setValue(True)

    if not fps_set:
        session = ftrack_api.Session()
        task = session.get("Task", os.environ["FTRACK_TASKID"])
        if "fps" in task["parent"]["custom_attributes"]:
            fps = task["parent"]["custom_attributes"]["fps"]

            msg = "{0}: Setting FPS to {1}."
            print msg.format(__file__, fps)
            nuke.root()["fps"].setValue(fps)


def resolutionInit():
    """
    Extecting a "width" and "height" custom attributes,
    on the parent entity of the task.

    Adds a "ftrackResolutionSet" knob to the root node in Nuke,
    which indicates whether to set the resolution on startup.
    """

    node = nuke.root()

    # Adding/Checking ftrack fps attribute
    resolution_set = False
    if "ftrackResolutionSet" in node.knobs():
        resolution_set = node["ftrackResolutionSet"].getValue()
    else:
        node.addKnob(nuke.Tab_Knob("Ftrack"))
        knob = nuke.Boolean_Knob(
            "ftrackResolutionSet", "Set Resolution on startup."
        )
        node.addKnob(knob)
        node["ftrackResolutionSet"].setValue(True)

    if not resolution_set:
        session = ftrack_api.Session()
        task = session.get("Task", os.environ["FTRACK_TASKID"])

        width = None
        if "width" in task["parent"]["custom_attributes"]:
            width = task["parent"]["custom_attributes"]["width"]
        height = None
        if "height" in task["parent"]["custom_attributes"]:
            height = task["parent"]["custom_attributes"]["height"]

        msg = "{0}: Setting Resolution to {1}x{2}."
        print msg.format(__file__, width, height)
        fmt = None
        for f in nuke.formats():
            if f.width() == width and f.height() == height:
                fmt = f

        if fmt:
            nuke.root()['format'].setValue(fmt.name())
        else:
            fmt = "{0} {1} FtrackDefault"
            nuke.addFormat(fmt)
            nuke.root()['format'].setValue("FtrackDefault")


def frameRangeInit():
    """
    Extecting a "fstart" and "fend" custom attributes,
    on the parent entity of the task.
    An "handles" optional custom attribute is also queried.

    Adds a "ftrackFrameRangeSet" knob to the root node in Nuke,
    which indicates whether to set the resolution on startup.
    """

    node = nuke.root()

    # Adding/Checking ftrack fps attribute
    frame_range_set = False
    if "ftrackFrameRangeSet" in node.knobs():
        frame_range_set = node["ftrackFrameRangeSet"].getValue()
    else:
        node.addKnob(nuke.Tab_Knob("Ftrack"))
        knob = nuke.Boolean_Knob(
            "ftrackFrameRangeSet", "Set Frame Range on startup."
        )
        node.addKnob(knob)
        node["ftrackFrameRangeSet"].setValue(True)

    if not frame_range_set:
        session = ftrack_api.Session()
        task = session.get("Task", os.environ["FTRACK_TASKID"])

        fstart = None
        if "fstart" in task["parent"]["custom_attributes"]:
            fstart = task["parent"]["custom_attributes"]["fstart"]
        fend = None
        if "fend" in task["parent"]["custom_attributes"]:
            fend = task["parent"]["custom_attributes"]["fend"]
        handles = 0
        if "handles" in task["parent"]["custom_attributes"]:
            handles = task["parent"]["custom_attributes"]["handles"]

        if fstart and fend:
            nuke.root()["first_frame"].setValue(fstart)
            last_frame = fend + (handles * 2)
            nuke.root()["last_frame"].setValue(last_frame)

            msg = "{0}: Setting Frame Range to {1}-{2}."
            print msg.format(__file__, fstart, last_frame)


def get_unused_components(session):

    # Get scene data
    component_names = []
    asset_ids = []
    for node in nuke.allNodes():
        knobs = node.knobs()
        if "assetId" in knobs:
            asset_ids.append(node["assetId"].getValue())
        if "componentName" in knobs:
            component_names.append(node["componentName"].getValue())

    # Skip if no existing assets are found
    if not component_names:
        return

    # Get all online components
    query = "Component where version.asset.id in ("
    for id in asset_ids:
        query += "\"{0}\",".format(id)
    query = query[:-1] + ")"

    data = {}
    components_data = {}
    for component in session.query(query):
        name = component["name"]

        # Skip components used in scene
        if name in component_names:
            continue

        # Skip versions that are lower than existing ones
        version = component["version"]["version"]
        if name in data and version < data[name]:
            continue

        data[name] = version

        # Overwrite with higher version components
        components_data[name] = component

    # Flatten component data to a list
    components = []
    for component in components_data.itervalues():
        components.append(component)

    return components


def import_components(components):

    for new_component in components:

        component = ftrack.Component(new_component["id"])
        assetversion = component.getVersion()
        asset = assetversion.getAsset()
        assettype = asset.getType()

        # Create node
        resultingNode = nuke.createNode('Read', inpanel=False)
        resultingNode['name'].setValue(
            HelpFunctions.safeString(asset.getName()) + '_' +
            HelpFunctions.safeString(component.getName())
        )

        # Add Ftrack tab
        knobs = resultingNode.knobs().keys()
        if 'ftracktab' not in knobs:
            # Note: the tab is supposed to be existing as it gets created
            # through callback during the read and write nodes creation.
            # This check is to ensure corner cases are handled properly.
            tab = nuke.Tab_Knob('ftracktab', 'ftrack')
            resultingNode.addKnob(tab)

        btn = nuke.String_Knob('componentId')
        resultingNode.addKnob(btn)
        btn = nuke.String_Knob('componentName')
        resultingNode.addKnob(btn)
        btn = nuke.String_Knob('assetVersionId')
        resultingNode.addKnob(btn)
        btn = nuke.String_Knob('assetVersion')
        resultingNode.addKnob(btn)
        btn = nuke.String_Knob('assetName')
        resultingNode.addKnob(btn)
        btn = nuke.String_Knob('assetType')
        resultingNode.addKnob(btn)
        btn = nuke.String_Knob('assetId')
        resultingNode.addKnob(btn)

        # Setup node
        file_path = component.getResourceIdentifier()
        resultingNode['file'].fromUserText(
            HelpFunctions.safeString(file_path)
        )

        members = component.getMembers()
        frames = [int(member.getName()) for member in members]
        start = min(frames)
        end = max(frames)

        resultingNode['first'].setValue(start)
        resultingNode['origfirst'].setValue(start)
        resultingNode['last'].setValue(end)
        resultingNode['origlast'].setValue(end)

        resultingNode.knob('assetId').setValue(
            HelpFunctions.safeString(asset.getId())
        )
        resultingNode.knob('componentId').setValue(
            HelpFunctions.safeString(component.getEntityRef())
        )
        resultingNode.knob('componentName').setValue(
            HelpFunctions.safeString(component.getName())
        )
        resultingNode.knob('assetVersionId').setValue(
            HelpFunctions.safeString(assetversion.getEntityRef())
        )
        resultingNode.knob('assetVersion').setValue(
            HelpFunctions.safeString(str(assetversion.getVersion()))
        )
        resultingNode.knob('assetName').setValue(
            HelpFunctions.safeString(asset.getName())
        )
        resultingNode.knob('assetType').setValue(
            HelpFunctions.safeString(assettype.getShort())
        )


def scan_for_unused_components():

    # Get components
    session = ftrack_api.Session()
    components = get_unused_components(session)
    if not components:
        return

    # Get details about components
    msg = ""
    msg_template = "task: {0}\nasset: {1}\nversion: {2}"
    msg_template += "\ncomponent: {3}\n\n"
    for component in components:

        # Getting Ftrack task path
        path = ""
        task = component["version"]["task"]
        for item in component["version"]["task"]["link"][:-1]:
            path += session.get(item["type"], item["id"])["name"] + "/"
        path += task["name"]

        # Adding component details
        msg += msg_template.format(
            path,
            component["version"]["asset"]["name"],
            component["version"]["version"],
            component["name"]
        )

    # Create message box
    msgBox = QtGui.QMessageBox()
    msgBox.setText("Unused components found.")
    msgBox.setDetailedText(msg)
    msgBox.setStandardButtons(
        QtGui.QMessageBox.Save | QtGui.QMessageBox.Cancel
    )
    msgBox.setDefaultButton(QtGui.QMessageBox.Save)
    button = msgBox.button(QtGui.QMessageBox.Save)
    button.setText("Import All")
    ret = msgBox.exec_()

    # Import components on request
    if ret == QtGui.QMessageBox.Save:
        import_components(components)


def init():
    nuke.addOnScriptLoad(fpsInit)
    nuke.addOnScriptLoad(resolutionInit)
    nuke.addOnScriptLoad(frameRangeInit)

    nuke.addOnScriptLoad(scan_for_unused_components)

    # Scan explicitly for new assets on startup,
    # since Ftrack native implementation only scans
    # when loading a script within Nuke.
    nuke.addOnScriptLoad(scan_for_new_assets)
