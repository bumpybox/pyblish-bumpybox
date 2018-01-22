import pyblish.api


class CollectNukeReads(pyblish.api.ContextPlugin):
    """Collect all read nodes."""

    order = pyblish.api.CollectorOrder
    label = "Reads"
    hosts = ["nuke", "nukeassist"]

    def process(self, context):
        import os

        import clique

        import nuke

        # creating instances per write node
        for node in nuke.allNodes():
            if node.Class() != "Read":
                continue

            if not node.metadata():
                continue

            # Determine output type
            output_type = "img"
            movie_formats = ["ari", "avi", "gif", "mov", "r3d"]
            if node.metadata()["input/filereader"] in movie_formats:
                output_type = "mov"
            scene_formats = ["psd"]
            if node.metadata()["input/filereader"] in scene_formats:
                output_type = "scene"

            # Create instance
            instance = context.create_instance(node.name())
            instance.data["families"] = [output_type, "local", "output"]
            instance.data["family"] = "read"
            instance.add(node)

            path = nuke.filename(node)

            # Adding/Checking publish attribute
            if "publish" not in node.knobs():
                knob = nuke.Boolean_Knob("publish", "Publish")
                knob.setValue(False)
                node.addKnob(knob)

            # Compare against selection
            selection = instance.context.data.get("selection", [])
            publish = bool(node["publish"].getValue())
            if selection:
                if list(set(instance) & set(selection)):
                    publish = True
                else:
                    publish = False

            instance.data["publish"] = publish

            # Collecting file paths
            label = "{0} - {1}".format(node.name(), os.path.basename(path))
            if output_type == "img":
                # This could be improved because it does not account for "#"
                # being in a sequence.
                if "#" in path:
                    padding = path.count("#")
                    path = path.replace(
                        "#" * padding, "%{0:0>2}d".format(padding)
                    )

                try:
                    collection = clique.parse(path + " []")
                except ValueError as e:
                    collections, remainder = clique.assemble(
                        [path],
                        minimum_items=1,
                        patterns=[clique.PATTERNS['frames']]
                    )

                    if collections:
                        collection = collections[0]
                    else:
                        context.remove(instance)
                        self.log.warning(
                            "Collection error on \"{0}\": "
                            "{1}".format(node.name(), e)
                        )
                        continue

                for f in os.listdir(os.path.dirname(path)):
                    file_path = os.path.join(os.path.dirname(path), f)
                    file_path = file_path.replace("\\", "/")
                    if collection.match(file_path):
                        collection.add(file_path)

                # Limit to frame range
                first = node["first"].value()
                last = node["last"].value()

                indexes = list(collection.indexes)
                collection.indexes.clear()
                collection.indexes.update(
                    set(indexes) & set([x for x in range(first, last + 1)])
                )

                instance.data["collection"] = collection
                label = "{0} - {1}".format(
                    node.name(), os.path.basename(collection.format())
                )
            else:
                instance.data["output_path"] = path

            instance.data["label"] = label

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
