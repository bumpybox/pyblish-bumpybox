from pyblish import api
from pyblish_bumpybox import inventory


class CollectNukeWrites(api.ContextPlugin):
    """Collect all write nodes."""

    order = inventory.get_order(__file__, "CollectNukeWrites")
    label = "Writes Royal Render"
    hosts = ["nuke", "nukeassist"]
    targets = ["process.royalrender"]

    def process(self, context):
        import nuke

        for item in context.data["write_instances"]:
            instance = context.create_instance(item.data["name"])
            for key, value in item.data.iteritems():
                instance.data[key] = value

            instance.data["label"] += " - royalrender"
            instance.data["families"] = ["write", "royalrender"]
            for node in item:
                instance.add(node)

            # Adding/Checking publish attribute
            if "process_royalrender" not in node.knobs():
                knob = nuke.Boolean_Knob(
                    "process_royalrender", "Process RoyalRender"
                )
                knob.setValue(False)
                node.addKnob(knob)

            value = bool(node["process_royalrender"].getValue())

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
                instance[0].removeKnob(instance[0]["process_royalrender"])
                knob = nuke.Boolean_Knob(
                    "process_royalrender", "Process RoyalRender"
                )
                knob.setValue(value)
                instance[0].addKnob(knob)

            instance.data["instanceToggled"] = instanceToggled


class CollectMayaSets(api.ContextPlugin):
    """Collect all local processing write instances."""

    order = inventory.get_order(__file__, "CollectMayaSets")
    label = "Sets Royal Render"
    hosts = ["maya"]
    targets = ["process.royalrender"]

    def process(self, context):

        for item in context.data["instances"]:
            # Skip any instances that is not valid.
            valid_families = ["alembic", "mayaAscii", "mayaBinary"]
            if len(set(valid_families) & set(item.data["families"])) != 1:
                continue

            instance = context.create_instance(item.data["name"])
            for key, value in item.data.iteritems():
                instance.data[key] = value

            instance.data["families"] += ["royalrender"]
            for node in item:
                instance.add(node)
