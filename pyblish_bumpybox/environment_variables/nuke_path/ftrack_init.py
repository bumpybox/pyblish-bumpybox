import os

import nuke

import ftrack_api
from ftrack_connect_nuke.ui.legacy import scan_for_new_assets
from pyblish_bumpybox.nuke import utils


def fps_init():
    """
    Sets the frame rate on first launch.

    Extracting a "fps" custom attribute on the parent entity of the task.

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


def resolution_init():
    """
    Sets the resolution on first launch.

    Extracting a "width" and "height" custom attributes,
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


def frame_range_init():
    """
    Sets the frame range on first launch.

    Extracting a "fstart" and "fend" custom attributes,
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


def lut_init():

    # Get published LUT, either on the current task or through parents.
    session = ftrack_api.Session()

    query = "Component where version.task_id is \"{0}\""
    query += " and version.asset.type.short is \"lut\""
    component = session.query(
        query.format(os.environ["FTRACK_TASKID"])
    ).first()

    if not component:
        task = session.get("Task", os.environ["FTRACK_TASKID"])
        query = "Component where version.asset.type.short is \"lut\""
        query += " and version.asset.parent.id is \"{0}\""
        for item in reversed(task["link"][:-2]):
            component = session.query(
                query.format(item["id"])
            ).first()
            if component:
                break

    if not component:
        print "{0}: Could not find any published LUTs.".format(__file__)
        return

    # Collect component data and Nuke display name.
    path = component["component_locations"][0]["resource_identifier"]
    colorspace_in = component["metadata"]["colorspace_in"]
    colorspace_out = component["metadata"]["colorspace_out"]

    display_name = ""
    for item in component["version"]["task"]["link"][:]:
        display_name += session.get(item['type'], item['id'])["name"] + "/"
    display_name = display_name[:-1]
    display_name += ": {0} > {1}".format(colorspace_in, colorspace_out)

    # Register the lut.
    values_syntax = {
        "linear": "linear",
        "srgb": "sRGB",
        "rec709": "rec709",
        "cineon": "Cineon",
        "gamma1.8": "Gamma1.8",
        "gamma2.2": "Gamma2.2",
        "gamma2.4": "Gamma2.4",
        "panalog": "Panalog",
        "redlog": "REDLog",
        "viperlog": "ViperLog",
        "alexav3logc": "AlexaV3LogC",
        "ploglin": "PLogLin",
        "slog": "SLog",
        "slog1": "SLog1",
        "slog2": "SLog2",
        "slog3": "SLog3",
        "clog": "CLog",
        "protune": "Protune",
        "redspace": "REDSpace"
    }

    node_data = "vfield_file {0} colorspaceIn {1} colorspaceOut {2}"
    nuke.ViewerProcess.register(
        display_name,
        nuke.createNode,
        (
            "Vectorfield",
            node_data.format(
                path.replace("\\", "/"),
                values_syntax[colorspace_in],
                values_syntax[colorspace_out]
            )
        )
    )

    # Adding viewerprocess callback
    nuke.addOnCreate(
        modify_viewer_node, args=(display_name), nodeClass="Viewer"
    )


# Nuke callback for modifying the viewer node on creation
def modify_viewer_node(viewerprocess):

    nuke.thisNode()["viewerProcess"].setValue(str(viewerprocess))


def init():

    # Adding scan_for_unused_components
    menubar = nuke.menu("Nuke")
    menu = menubar.menu("pyblish-bumpybox")
    cmd = "from pyblish_bumpybox.nuke import utils;"
    cmd += "utils.scan_for_unused_components()"
    menu.addCommand("Scan for unused components", cmd)

    # Adding published LUT
    lut_init()

    # pyblish-bumpybox callbacks
    nuke.addOnScriptLoad(fps_init)
    nuke.addOnScriptLoad(resolution_init)
    nuke.addOnScriptLoad(frame_range_init)
    nuke.addOnScriptLoad(utils.scan_for_unused_components)

    # Scan explicitly for new assets on startup,
    # since Ftrack native implementation only scans
    # when loading a script within Nuke.
    nuke.addOnScriptLoad(scan_for_new_assets)
