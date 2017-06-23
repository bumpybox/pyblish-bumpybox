import pyblish.api


class CollectHieroNukeStudioTasks(pyblish.api.ContextPlugin):
    """Collect all tasks from submission."""

    order = pyblish.api.CollectorOrder
    label = "Tasks"
    hosts = ["nukestudio"]

    def process(self, context):
        import os

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
            name = os.path.splitext(os.path.basename(resolved_path))[0]
            instance = context.create_instance(name=name)
            instance.add(task)

            instance.data["family"] = "task"
            instance.data["families"] = [asset_type, "local"]

            project_root = context.data["activeProject"].projectRoot()
            relative_path = resolved_path.replace(project_root, "")
            label = "{0} - {1} - local".format(relative_path, asset_type)
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
                instance.data["output"] = resolved_path
