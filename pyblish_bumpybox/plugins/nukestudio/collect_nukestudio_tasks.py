import pyblish.api


class CollectHieroNukeStudioTasks(pyblish.api.ContextPlugin):
    """Collect all tasks from submission."""

    order = pyblish.api.CollectorOrder
    label = "Tasks"
    hosts = ["nukestudio"]

    def process(self, context):
        import os
        import re

        import hiero.exporters as he
        import clique

        for task in context.data["submission"].getLeafTasks():

            # Skip audio track items
            media_type = "core.Hiero.Python.TrackItem.MediaType.kAudio"
            if str(task._item.mediaType()) == media_type:
                continue

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

            # Formatting the basename to not include frame padding or "."
            name = os.path.basename(resolved_path)
            name = name.replace("#", "").replace(".", "_")
            name = re.sub(r"%.*d", "_", name)
            name = re.sub(r"_{2,}", "_", name)
            instance = context.create_instance(name=name)

            instance.add(task)

            instance.data["family"] = "task"
            instance.data["families"] = [asset_type, "local"]

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
