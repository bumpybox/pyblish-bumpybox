import os
import time
import threading

import pyblish_integration


if os.environ['PYBLISHPLUGINPATH'] != os.environ['ASSETMANAGERPLUGINPATH']:
    os.environ['PYBLISHPLUGINPATH_BACKUP'] = os.environ['PYBLISHPLUGINPATH']

os.environ['PYBLISHPLUGINPATH'] = os.environ['ASSETMANAGERPLUGINPATH']

pyblish_integration.show()

def reset_environment():
    time.sleep(10)

    os.environ['PYBLISHPLUGINPATH'] = os.environ['PYBLISHPLUGINPATH_BACKUP']

thread = threading.Thread(target=reset_environment, args=())
thread.daemon = True
thread.start()
