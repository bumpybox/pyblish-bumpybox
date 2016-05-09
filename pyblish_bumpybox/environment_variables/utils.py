import os
import json
import base64


def getFtrackTaskId():
    decodedEventData = json.loads(
        base64.b64decode(
            os.environ.get('FTRACK_CONNECT_EVENT')
        )
    )

    return decodedEventData.get('selection')[0]['entityId']


def getFtrackContextPath():
    try:
        import ftrack
    except:
        print "'ftrack' module not present. Can't set Pyblish window."
        return

    task = ftrack.Task(getFtrackTaskId())
    path = [task.getName()]
    for p in task.getParents():
        path.append(p.getName())

    return ' / '.join(list(reversed(path)))
