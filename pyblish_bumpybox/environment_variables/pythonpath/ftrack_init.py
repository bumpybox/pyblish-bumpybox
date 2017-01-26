import os

import pymel.core
import ftrack


def resolutionInit():
    defaultResolution = pymel.core.PyNode("defaultResolution")
    task = ftrack.Task(os.environ["FTRACK_TASKID"])

    width = task.getParent().get("width")
    defaultResolution.width.set(width)
    pymel.core.warning("Changed resolution width to: {0}".format(width))
    height = task.getParent().get("height")
    defaultResolution.height.set(height)
    pymel.core.warning("Changed resolution height to: {0}".format(height))


def init():
    pymel.core.evalDeferred("ftrack_init.resolutionInit()")
