import pyblish.api


class ExtractHieroNukeStudioTask(pyblish.api.InstancePlugin):
    """Extract tasks."""

    order = pyblish.api.ExtractorOrder
    label = "Tasks"
    hosts = ["nukestudio"]
    families = ["task"]

    def process(self, instance):
        import time
        import os

        import hiero.core.nuke as nuke

        task = instance[0]
        task.startTask()
        while task.taskStep():
            time.sleep(1)

        families = instance.data["families"]
        if "mov" in families or "img" in families:
            script_path = instance[0]._scriptfile
            log_path = script_path.replace(".nk", ".log")
            log_file = open(log_path, "w")
            process = nuke.executeNukeScript(script_path, log_file, True)

            self.poll(process)

            log_file.close()

            if not instance[0]._preset.properties()["keepNukeScript"]:
                os.remove(script_path)
                os.remove(log_path)

        # Fill collection with output
        if "img" in families:
            collection = instance.data["collection"]
            path = os.path.dirname(collection.format())
            for f in os.listdir(path):
                file_path = os.path.join(path, f).replace("\\", "/")
                if collection.match(file_path):
                    collection.add(file_path)

    def poll(self, process):
        import time

        returnCode = process.poll()

        # if the return code hasn't been set, Nuke is still running
        if returnCode is None:
            time.sleep(1)

            self.poll(process)
