import os

import pyblish_qml
import ftrack


# setting Pyblish Window title
def setPyblishWindowTitle():
    task = ftrack.Task(os.environ['FTRACK_TASKID'])
    path = [task.getName()]
    for p in task.getParents():
        path.append(p.getName())

    path = ' / '.join(list(reversed(path)))
    pyblish_qml.settings.WindowTitle = path

setPyblishWindowTitle()
