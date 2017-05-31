import os

import pymel.core as pm
import maya.cmds as mc
import ftrack
import ftrack_api


def resolution_init():
    """
    Sets the resolution on first launch.

    Extracting a "width" and "height" custom attributes,
    on the parent entity of the task.

    Adds a "ftrackResolutionSet" attribute to the defaultResolution node,
    which indicates whether to set the resolution on startup.
    """

    defaultResolution = pm.PyNode("defaultResolution")
    task = ftrack.Task(os.environ["FTRACK_TASKID"])

    # Adding/Checking ftrack resolution attribute
    resolution_set = False
    if hasattr(defaultResolution, "ftrackResolutionSet"):
        attr = pm.Attribute("defaultResolution.ftrackResolutionSet")
        resolution_set = attr.get()
    else:
        pm.addAttr(
            defaultResolution,
            longName="ftrackResolutionSet",
            defaultValue=True,
            attributeType="bool"
        )

    if not resolution_set:
        width = task.getParent().get("width")
        defaultResolution.width.set(width)
        pm.warning("Changed resolution width to: {0}".format(width))
        height = task.getParent().get("height")
        defaultResolution.height.set(height)
        pm.warning("Changed resolution height to: {0}".format(height))

        # Vray specific resolution
        if pm.objExists("vraySettings"):
            vray_settings = pm.PyNode("vraySettings")
            vray_settings.width.set(width)
            pm.warning("Changed vray resolution width to: {0}".format(width))
            vray_settings.height.set(height)
            pm.warning("Changed vray resolution height to: {0}".format(height))


def render_range_init():
    """
    Sets the render settings frame range on first launch.

    Extracting a "fstart", "fend" and "handles" custom attributes,
    from the parent entity of the task.

    Adds a "ftrackFrameRangeSet" attribute to the defaultRenderGlobals node,
    which indicates whether to set the resolution on startup.
    """

    # Adding/Checking ftrack render range attribute
    defaultRenderGlobals = pm.PyNode("defaultRenderGlobals")
    render_range_set = False
    if hasattr(defaultRenderGlobals, "ftrackRenderRangeSet"):
        attr = pm.Attribute("defaultRenderGlobals.ftrackRenderRangeSet")
        render_range_set = attr.get()
    else:
        pm.addAttr(
            defaultRenderGlobals,
            longName="ftrackRenderRangeSet",
            defaultValue=True,
            attributeType="bool"
        )

    if not render_range_set:

        task = ftrack.Task(os.environ["FTRACK_TASKID"])

        startFrame = float(task.getParent().get("fstart"))
        endFrame = float(task.getParent().get("fend"))

        handles = float(task.getParent().get("handles"))

        mc.warning(
            "Setting render range to {0} {1} ".format(startFrame, endFrame)
        )

        # Add handles to start and end frame
        hsf = startFrame - handles
        hef = endFrame + handles

        defaultRenderGlobals.animation.set(True)
        defaultRenderGlobals.animationRange.set(1)
        defaultRenderGlobals.startFrame.set(hsf)
        defaultRenderGlobals.endFrame.set(hef)

        # Vray specific resolution
        if pm.objExists("vraySettings"):
            vray_settings = pm.PyNode("vraySettings")
            vray_settings.animType.set(1)


def disable_debug():
    import logging
    logging.getLogger().setLevel(logging.INFO)


def init():
    pm.evalDeferred("ftrack_init.resolution_init()", lowestPriority=True)
    pm.evalDeferred("ftrack_init.render_range_init()", lowestPriority=True)

    # Disabling debug logging, cause of FTrack constant stream of print outs.
    mc.evalDeferred("ftrack_init.disable_debug()", lowestPriority=True)

    # pyblish-qml settings
    try:
        __import__("pyblish_qml")
    except ImportError as e:
        print("pyblish-bumpybox: Could not load pyblish-qml: %s " % e)
    else:
        from pyblish_qml import settings

        session = ftrack_api.Session()
        task = session.get("Task", os.environ["FTRACK_TASKID"])
        ftrack_path = ""
        for item in task["link"]:
            ftrack_path += session.get(item["type"], item["id"])["name"]
            ftrack_path += " / "
        settings.WindowTitle = ftrack_path[:-3]
