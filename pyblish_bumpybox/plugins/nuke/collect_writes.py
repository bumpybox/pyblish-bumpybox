from pyblish import api
from pyblish_bumpybox import inventory


class CollectWrites(api.ContextPlugin):
    """Collect all write nodes."""

    order = inventory.get_order(__file__, "CollectWrites")
    label = "Writes"
    hosts = ["nuke", "nukeassist"]
    targets = ["default", "process"]

    def process(self, context):
        import clique

        import nuke

        instances = []
        # creating instances per write node
        for node in nuke.allNodes():
            if node.Class() != "Write":
                continue

            # Determine output type
            output_type = "img"
            if node["file_type"].value() == "mov":
                output_type = "mov"

            # Create instance
            instance = plugin.Instance(node.name())
            instance.data["family"] = output_type
            instance.add(node)

            instance.data["label"] = node.name()

            instance.data["publish"] = False

            # Get frame range
            start_frame = int(nuke.root()["first_frame"].getValue())
            end_frame = int(nuke.root()["last_frame"].getValue())
            if node["use_limit"].getValue():
                start_frame = int(node["first"].getValue())
                end_frame = int(node["last"].getValue())

            # Add collection
            collection = None
            try:
                path = ""
                if nuke.filename(node):
                    path = nuke.filename(node)
                path += " [{0}-{1}]".format(start_frame, end_frame)
                collection = clique.parse(path)
            except ValueError:
                # Ignore the exception when the path does not match the
                # collection.
                pass

            instance.data["collection"] = collection

            instances.append(instance)

        context.data["write_instances"] = instances

        context.data["instances"] = (
            context.data.get("instances", []) + instances
        )


class CollectWritesProcess(api.ContextPlugin):
    """Collect all local processing write instances."""

    order = inventory.get_order(__file__, "CollectWritesProcess")
    label = "Writes Local"
    hosts = ["nuke"]
    targets = ["process.local"]

    def process(self, context):
        import nuke

        for item in context.data["write_instances"]:
            instance = context.create_instance(item.data["name"])
            for key, value in item.data.iteritems():
                instance.data[key] = value

            instance.data["label"] += " - write - local"
            instance.data["families"] = ["write", "local"]
            for node in item:
                instance.add(node)

            # Adding/Checking publish attribute
            if "process_local" not in node.knobs():
                knob = nuke.Boolean_Knob(
                    "process_local", "Process Local"
                )
                knob.setValue(False)
                node.addKnob(knob)

            value = bool(node["process_local"].getValue())

            # Compare against selection
            selection = instance.context.data.get("selection", [])
            if selection:
                if list(set(instance) & set(selection)):
                    value = True
                else:
                    value = False

            instance.data["publish"] = value

            def instanceToggled(instance, value):
                instance[0]["process_local"].setValue(value)

            instance.data["instanceToggled"] = instanceToggled


class CollectWritesPublish(api.ContextPlugin):
    """Collect all write instances for publishing."""

    order = inventory.get_order(__file__, "CollectWritesPublish")
    label = "Writes"
    hosts = ["nuke", "nukeassist"]
    targets = ["default"]

    def process(self, context):
        import os

        import nuke

        for item in context.data["write_instances"]:

            # If the collection was not generated.
            if not item.data["collection"]:
                continue

            missing_files = []
            for f in item.data["collection"]:
                if not os.path.exists(f):
                    missing_files.append(f)

            for f in missing_files:
                item.data["collection"].remove(f)

            if not list(item.data["collection"]):
                continue

            instance = context.create_instance(item.data["name"])
            for key, value in item.data.iteritems():
                instance.data[key] = value

            instance.data["families"] = ["output"]
            instance.data["label"] += (
                " - " + os.path.basename(instance.data["collection"].format())
            )

            for node in item:
                instance.add(node)

            # Adding/Checking publish attribute
            if "publish" not in node.knobs():
                knob = nuke.Boolean_Knob(
                    "publish", "Publish"
                )
                knob.setValue(False)
                node.addKnob(knob)

            value = bool(node["publish"].getValue())

            # Compare against selection
            selection = instance.context.data.get("selection", [])
            if selection:
                if list(set(instance) & set(selection)):
                    value = True
                else:
                    value = False

            instance.data["publish"] = value

            def instanceToggled(instance, value):
                # Removing and adding the knob to support NukeAssist, where
                # you can't modify the knob value directly.
                instance[0].removeKnob(instance[0]["publish"])
                knob = nuke.Boolean_Knob(
                    "publish", "Publish"
                )
                knob.setValue(value)
                instance[0].addKnob(knob)

            instance.data["instanceToggled"] = instanceToggled
