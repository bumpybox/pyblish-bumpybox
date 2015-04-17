import os
import tempfile
import subprocess
import getpass

import nuke
import nukescripts
import pyblish.api


@pyblish.api.log
class SubmitDeadline(pyblish.api.Extractor):
    """Submits the scene to Deadline"""

    families = ['writeNode']
    hosts = ['nuke']
    version = (0, 1, 0)
    optional = True

    def process_instance(self, instance):

        # submitting job
        args = []
        args.append(instance.data('job_path'))
        args.append(instance.data('plugin_path'))
        args.append(instance.data('scene_file'))

        self.log.info(self.CallDeadlineCommand(args))

    def CallDeadlineCommand(self, arguments, hideWindow=True):
        # On OSX, we look for the DEADLINE_PATH file. On other platforms, we use the environment variable.
        if os.path.exists( "/Users/Shared/Thinkbox/DEADLINE_PATH" ):
            with open( "/Users/Shared/Thinkbox/DEADLINE_PATH" ) as f: deadlineBin = f.read().strip()
            deadlineCommand = deadlineBin + "/deadlinecommand"
        else:
            deadlineBin = os.environ['DEADLINE_PATH']
            if os.name == 'nt':
                deadlineCommand = deadlineBin + "\\deadlinecommand.exe"
            else:
                deadlineCommand = deadlineBin + "/deadlinecommand"

        startupinfo = None
        if hideWindow and os.name == 'nt' and hasattr( subprocess, 'STARTF_USESHOWWINDOW' ):
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        environment = {}
        for key in os.environ.keys():
            environment[key] = str(os.environ[key])

        # Need to set the PATH, cuz windows seems to load DLLs from the PATH earlier that cwd....
        if os.name == 'nt':
            environment['PATH'] = str(deadlineBin + os.pathsep + os.environ['PATH'])

        arguments.insert( 0, deadlineCommand)

        # Specifying PIPE for all handles to workaround a Python bug on Windows. The unused handles are then closed immediatley afterwards.
        proc = subprocess.Popen(arguments, cwd=deadlineBin, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo, env=environment)
        proc.stdin.close()
        proc.stderr.close()

        output = proc.stdout.read()

        return output
