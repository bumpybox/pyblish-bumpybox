import nuke

import ftrack
import ftrack_api
from ftrack_connect.connector import HelpFunctions
from Qt import QtGui


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
