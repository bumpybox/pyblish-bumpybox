import pyblish.api


class CollectHieroNukeStudioTrackItems(pyblish.api.ContextPlugin):
    """Collect all tasks from submission."""

    order = pyblish.api.CollectorOrder
    label = "Track Items"
    hosts = ["nukestudio"]

    def process(self, context):

        submission = context.data.get("submission", None)
        if not submission:
            return

        data = {}
        for task in submission.getLeafTasks():

            # Skip audio track items
            media_type = "core.Hiero.Python.TrackItem.MediaType.kAudio"
            if str(task._item.mediaType()) == media_type:
                continue

            item = task._item
            if item.name() not in data:
                data[item.name()] = {"item": item, "tasks": [task]}
            else:
                data[item.name()]["tasks"].append(task)

        for key, value in data.iteritems():

            instance = context.create_instance(name=key)
            instance.add(value["item"])

            instance.data["family"] = "trackItem"

            instance.data["tasks"] = value["tasks"]
