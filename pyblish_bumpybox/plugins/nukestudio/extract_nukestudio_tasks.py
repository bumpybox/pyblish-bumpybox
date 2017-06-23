import pyblish.api


class ExtractHieroNukeStudioTask(pyblish.api.InstancePlugin):
    """Extract tasks."""

    order = pyblish.api.ExtractorOrder
    label = "Tasks"
    hosts = ["nukestudio"]
    families = ["task"]

    def process(self, instance):
        import time

        task = instance[0]
        task.startTask()
        while task.taskStep():
            time.sleep(1)


class ExtractHierNukeStudioTranscode(pyblish.api.InstancePlugin):
    """Extract transcode."""

    order = ExtractHieroNukeStudioTask.order + 0.1
    label = "Transcode"
    hosts = ["hiero", "nukestudio"]
    families = ["img", "mov"]

    def process(self, instance):
        import os

        import hiero.core.nuke as nuke

        script_path = instance[0]._scriptfile
        log_path = script_path.replace(".nk", ".log")
        log_file = open(log_path, "w")
        process = nuke.executeNukeScript(script_path, log_file, True)

        self.poll(process)

        log_file.close()

        if not instance[0]._preset.properties()["keepNukeScript"]:
            os.remove(script_path)
            os.remove(log_path)

    def poll(self, process):
        import time

        returnCode = process.poll()

        # if the return code hasn't been set, Nuke is still running
        if returnCode is None:
            time.sleep(1)

            self.poll(process)
