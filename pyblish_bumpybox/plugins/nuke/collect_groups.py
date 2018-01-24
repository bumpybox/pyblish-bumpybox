import pyblish.api


class CollectGroups(pyblish.api.ContextPlugin):
    """Collect all group nodes.

    Offset to get context.data["currentFile"]
    """

    order = pyblish.api.CollectorOrder + 0.1
    label = "Groups"
    hosts = ["nuke", "nukeassist"]

    def process(self, context):
        import os

        import nuke

        # creating instances per write node
        for node in nuke.allNodes():
            if node.Class() != "Group":
                continue

            # Add an instance per format supported.
            for fmt in ["lut", "gizmo"]:

                name = node["name"].getValue()
                instance = context.create_instance(name=name)
                instance.add(node)

                instance.data["families"] = [fmt, "group", "local"]
                instance.data["family"] = fmt

                label = "{0} - {1} - {2}".format(name, fmt, "local")
                instance.data["label"] = label

                # Adding/Checking publish attribute
                if fmt not in node.knobs():
                    knob = nuke.Boolean_Knob(fmt, fmt.title())
                    knob.setValue(False)
                    node.addKnob(knob)

                # Compare against selection
                selection = instance.context.data.get("selection", [])
                publish_state = bool(node[fmt].getValue())
                if selection:
                    if list(set(instance) & set(selection)):
                        publish_state = True
                    else:
                        publish_state = False

                instance.data["publish"] = publish_state

                # Generate output path
                directory = os.path.join(
                    os.path.dirname(instance.context.data["currentFile"]),
                    "workspace"
                )
                scene_name = os.path.splitext(
                    os.path.basename(instance.context.data["currentFile"])
                )[0]
                family = list(
                    set(["lut", "gizmo"]).intersection(
                        instance.data["families"]
                    )
                )[0]
                instance.data["output_path"] = os.path.join(
                    directory,
                    "{0}_{1}_{2}.gizmo".format(
                        scene_name, instance.data["name"], family
                    )
                )

                def instanceToggled(instance, value):
                    if "gizmo" in instance.data["families"]:
                        instance[0]["gizmo"].setValue(value)

                    if "lut" in instance.data["families"]:
                        instance[0]["lut"].setValue(value)

                instance.data["instanceToggled"] = instanceToggled
