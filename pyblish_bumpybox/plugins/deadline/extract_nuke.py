import math

import nuke
import pyblish.api


class BumpyboxDeadlineExtractNuke(pyblish.api.InstancePlugin):
    """ Appending Deadline data to deadline instances. """

    families = ["deadline"]
    order = pyblish.api.ExtractorOrder
    label = "Deadline"
    hosts = ["nuke"]

    def process(self, instance):

        node = instance[0]
        collection = instance.data["collection"]

        job_data = {}
        plugin_data = {}
        if "deadlineData" in instance.data:
            job_data = instance.data["deadlineData"]["job"].copy()
            plugin_data = instance.data["deadlineData"]["plugin"].copy()

        # Setting job data.
        job_data["Plugin"] = "Nuke"

        # Replace houdini frame padding with Deadline padding
        fmt = "{head}" + "#" * collection.padding + "{tail}"
        job_data["OutputFilename0"] = collection.format(fmt)
        job_data["Priority"] = instance.data["deadlinePriority"]
        job_data["Pool"] = instance.data["deadlinePool"]
        job_data["ConcurrentTasks"] = instance.data["deadlineConcurrentTasks"]

        # Get frame range
        node = instance[0]
        first_frame = nuke.root()["first_frame"].value()
        last_frame = nuke.root()["last_frame"].value()

        if node["use_limit"].value():
            first_frame = node["first"].value()
            last_frame = node["last"].value()

        job_data["Frames"] = "{0}-{1}".format(first_frame, last_frame)

        # Chunk size
        job_data["ChunkSize"] = instance.data["deadlineChunkSize"]
        if len(list(collection)) == 1:
            job_data["ChunkSize"] = str(last_frame)
        else:
            tasks = last_frame - first_frame + 1.0
            chunks = (last_frame - first_frame + 1.0) / job_data["ChunkSize"]
            # Deadline can only handle 5000 tasks maximum
            if tasks > 5000 and chunks > 5000:
                job_data["ChunkSize"] = str(int(math.ceil(tasks / 5000.0)))

        # Setting plugin data
        plugin_data["SceneFile"] = instance.context.data["currentFile"]

        # Setting data
        data = {
            "job": job_data,
            "plugin": plugin_data,
            "auxiliaryFiles": instance.context.data["currentFile"]
        }
        instance.data["deadlineData"] = data
