import nuke
import pyblish.api


class CollectNukeWriteGeo(pyblish.api.ContextPlugin):
    """Collect all write nodes."""

    order = pyblish.api.CollectorOrder
    label = "Write Geo"
    hosts = ["nuke"]
    targets = ["default", "process.local"]

    def process(self, context):

        instances = []
        # creating instances per write node
        for node in nuke.allNodes():
            if node.Class() != "WriteGeo":
                continue

            # Determine output type
            output_type = "cache"

            # Create instance
            instance = pyblish.api.Instance(node.name())
            instance.data["family"] = output_type
            instance.add(node)
            instance.data["label"] = "{0} - writegeo".format(node.name())
            instance.data["publish"] = False
            instance.data["output_path"] = nuke.filename(node)

            instances.append(instance)

        context.data["writegeo_instances"] = instances

        context.data["instances"] = (
            context.data.get("instances", []) + instances
        )


class CollectNukeWriteGeoLocal(pyblish.api.ContextPlugin):
    """Collect all local processing writegeo instances."""

    order = CollectNukeWriteGeo.order + 0.01
    label = "Write Geo Local"
    hosts = ["nuke"]
    targets = ["process.local"]

    def process(self, context):

        for item in context.data["writegeo_instances"]:
            instance = context.create_instance(item.data["name"])
            for key, value in item.data.iteritems():
                instance.data[key] = value

            instance.data["label"] += " - local"
            instance.data["families"] = ["writegeo", "local"]
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
            instance.data["publish"] = value
