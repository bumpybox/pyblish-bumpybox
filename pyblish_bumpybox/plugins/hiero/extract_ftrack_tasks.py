import traceback

import pyblish.api
import ftrack


class BumpyboxHieroExtractFtrackTasks(pyblish.api.Extractor):
    """ Extract Ftrack tasks.

    Offset to get shot from "extract_ftrack_shot"
    """

    families = ["task"]
    label = "Ftrack Tasks"
    optional = True
    order = pyblish.api.ExtractorOrder + 0.1

    def getTaskTypeByName(self, name):
        for t in ftrack.getTaskTypes():
            if t.getName().lower() == name.lower():
                return t

        return None

    def process(self, instance):

        for tag in instance.data["tagsData"]:
            if "task" == tag.get("tag.family", ""):
                task_name = tag["tag.label"]

                task_type = self.getTaskTypeByName(task_name)
                try:
                    shot = instance.data["ftrackShot"]
                    shot.createTask(task_name.lower(), taskType=task_type)
                except:
                    self.log.error(traceback.format_exc())
