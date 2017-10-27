import pyblish.api


class CollectNukeBackdrops(pyblish.api.ContextPlugin):
    """Collect all backdrop nodes.

    Offset to get context.data["currentFile"]
    """

    order = pyblish.api.CollectorOrder + 0.1
    label = "Backdrops"
    hosts = ["nuke"]

    def process(self, context):
        import os
        import nuke

        # creating instances per backdrop node
        for node in nuke.allNodes():
            if node.Class() != "BackdropNode":
                continue

            name = node["name"].getValue()
            instance = context.create_instance(name=name)
            instance.add(node)

            instance.data["families"] = ["local", "backdrop"]
            instance.data["family"] = "scene"

            label = "{0} - {1} - {2}".format(name, "scene", "local")
            instance.data["label"] = label

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

            # Generate output path
            directory = os.path.join(
                os.path.dirname(instance.context.data["currentFile"]),
                "workspace"
            )
            scene_name = os.path.splitext(
                os.path.basename(instance.context.data["currentFile"])
            )[0]
            instance.data["output_path"] = os.path.join(
                directory,
                "{0}_{1}.nk".format(scene_name, instance.data["name"])
            )

            def instanceToggled(instance, value):
                if instance[0].Class() == "BackdropNode":
                    instance[0]["publish"].setValue(value)

            instance.data["instanceToggled"] = instanceToggled
