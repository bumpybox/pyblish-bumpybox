import pyblish.api


class CollectNukeStudioTrackItems(pyblish.api.ContextPlugin):
    """Collect all tasks from submission."""

    order = pyblish.api.CollectorOrder
    label = "Track Items"
    hosts = ["nukestudio"]

    def process(self, context):
        submission = context.data.get("submission", None)
        data = {}

        # Set handles
        handles = 0
        if submission:
            for task in submission.getLeafTasks():

                if task._cutHandles:
                    handles = task._cutHandles

                # Skip audio track items
                media_type = "core.Hiero.Python.TrackItem.MediaType.kAudio"
                if str(task._item.mediaType()) == media_type:
                    continue

                item = task._item
                if item.name() not in data:
                    data[item.name()] = {"item": item, "tasks": [task]}
                else:
                    data[item.name()]["tasks"].append(task)

                data[item.name()]["startFrame"] = task.outputRange()[0]
                data[item.name()]["endFrame"] = task.outputRange()[1]
        else:
            for item in context.data.get("selection", []):
                # Skip audio track items
                media_type = "core.Hiero.Python.TrackItem.MediaType.kAudio"
                if str(item.mediaType()) == media_type:
                    continue

                data[item.name()] = {
                    "item": item,
                    "tasks": [],
                    "startFrame": item.timelineIn(),
                    "endFrame": item.timelineOut()
                }

        for key, value in data.iteritems():

            context.create_instance(
                name=key,
                item=value["item"],
                family="trackItem",
                tasks=value["tasks"],
                startFrame=value["startFrame"] + handles,
                endFrame=value["endFrame"] - handles,
                handles=handles
            )


class CollectNukeStudioTasks(pyblish.api.ContextPlugin):
    """Collect all tasks from submission."""

    order = CollectNukeStudioTrackItems.order + 0.01
    label = "Tasks"
    hosts = ["nukestudio"]

    def process(self, context):
        import os
        import re

        import hiero.exporters as he
        import clique

        for parent in context:
            if "trackItem" != parent.data["family"]:
                continue

            for task in parent.data["tasks"]:
                asset_type = None

                hiero_cls = he.FnTranscodeExporter.TranscodeExporter
                if isinstance(task, hiero_cls):
                    asset_type = "img"
                    if task.resolvedExportPath().endswith(".mov"):
                        asset_type = "mov"

                hiero_cls = he.FnNukeShotExporter.NukeShotExporter
                if isinstance(task, hiero_cls):
                    asset_type = "scene"

                hiero_cls = he.FnAudioExportTask.AudioExportTask
                if isinstance(task, hiero_cls):
                    asset_type = "audio"

                # Skip all non supported export types
                if not asset_type:
                    continue

                resolved_path = task.resolvedExportPath()

                # Formatting the basename to not include frame padding or
                # "."
                name = os.path.basename(resolved_path)
                name = name.replace("#", "").replace(".", "_")
                name = re.sub(r"%.*d", "_", name)
                name = re.sub(r"_{2,}", "_", name)
                instance = context.create_instance(name=name, parent=parent)

                instance.data["task"] = task
                instance.data["item"] = parent.data["item"]

                instance.data["family"] = "trackItem.task"
                instance.data["families"] = [asset_type, "local", "task"]

                label = "{0} - {1} - local".format(name, asset_type)
                instance.data["label"] = label

                # Add collection or output
                if asset_type == "img":
                    collection = None

                    if "#" in resolved_path:
                        head = resolved_path.split("#")[0]
                        padding = resolved_path.count("#")
                        tail = resolved_path.split("#")[-1]

                        collection = clique.Collection(
                            head=head, padding=padding, tail=tail
                        )

                    if "%" in resolved_path:
                        collection = clique.parse(
                            resolved_path, pattern="{head}{padding}{tail}"
                        )

                    if collection:
                        instance.data["collection"] = collection
                else:
                    instance.data["output_path"] = resolved_path
