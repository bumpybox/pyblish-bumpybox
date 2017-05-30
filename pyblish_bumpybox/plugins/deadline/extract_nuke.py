import math

import nuke
import pyblish.api


class BumpyboxDeadlineExtractNuke(pyblish.api.InstancePlugin):
    """ Appending Deadline data to deadline instances.

    Important that Path Mapping is turned off in the Nuke plugin.
    """

    families = ["deadline"]
    order = pyblish.api.ExtractorOrder
    label = "Deadline"
    hosts = ["nuke"]

    def process(self, instance):

        node = instance[0]
        collection = instance.data["collection"]

        data = instance.data.get("deadlineData", {"job": {}, "plugin": {}})

        # Setting job data.
        data["job"]["Plugin"] = "Nuke"
        data["job"]["Priority"] = int(instance.data["deadlinePriority"])
        data["job"]["Pool"] = instance.data["deadlinePool"]
        data["job"]["ConcurrentTasks"] = int(
            instance.data["deadlineConcurrentTasks"]
        )
        data["job"]["LimitGroups"] = instance.data["deadlineLimits"]

        # Replace houdini frame padding with Deadline padding
        fmt = "{head}" + "#" * collection.padding + "{tail}"
        data["job"]["OutputFilename0"] = collection.format(fmt)

        # Get frame range
        node = instance[0]
        first_frame = nuke.root()["first_frame"].value()
        last_frame = nuke.root()["last_frame"].value()

        if node["use_limit"].value():
            first_frame = node["first"].value()
            last_frame = node["last"].value()

        data["job"]["Frames"] = "{0}-{1}".format(
            int(first_frame), int(last_frame)
        )

        # Chunk size
        data["job"]["ChunkSize"] = int(instance.data["deadlineChunkSize"])
        if len(list(collection)) == 1:
            data["job"]["ChunkSize"] = str(int(last_frame))
        else:
            tasks = last_frame - first_frame + 1.0
            chunks = last_frame - first_frame + 1.0
            chunks /= data["job"]["ChunkSize"]
            # Deadline can only handle 5000 tasks maximum
            if tasks > 5000 and chunks > 5000:
                data["job"]["ChunkSize"] = str(int(math.ceil(tasks / 5000.0)))

        # Setting plugin data
        data["plugin"]["SceneFile"] = instance.context.data["currentFile"]
        data["plugin"]["EnforceRenderOrder"] = True
        data["plugin"]["WriteNode"] = node.name()
        data["plugin"]["NukeX"] = nuke.env["nukex"]
        data["plugin"]["Version"] = nuke.NUKE_VERSION_STRING.split("v")[0]
        data["plugin"]["EnablePathMapping"] = False

        # Setting data
        instance.data["deadlineData"] = data
