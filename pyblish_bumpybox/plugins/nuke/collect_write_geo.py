import pyblish.api


class CollectWriteGeo(pyblish.api.ContextPlugin):
    """Collect all write nodes."""

    order = pyblish.api.CollectorOrder
    label = "Write Geo"
    hosts = ["nuke"]
    targets = ["default", "process.local"]

    def process(self, context):
        import os

        import nuke

        instances = []
        # creating instances per write node
        for node in nuke.allNodes():
            if node.Class() != "WriteGeo":
                continue

            # Create cache instance
            instance = pyblish.api.Instance(node.name())
            instance.data["family"] = "cache"
            instance.data["families"] = ["writegeo"]
            instance.add(node)
            instance.data["label"] = node.name()
            instance.data["publish"] = False
            instance.data["output_path"] = nuke.filename(node)
            instances.append(instance)

            # Create camera instance
            instance = pyblish.api.Instance(node.name())
            instance.data["family"] = "camera"
            instance.data["families"] = ["writegeo"]
            instance.add(node)
            instance.data["label"] = node.name()
            instance.data["publish"] = False
            path, ext = os.path.splitext(nuke.filename(node))
            instance.data["output_path"] = "{0}_camera{1}".format(path, ext)
            instances.append(instance)

            # Create geometry instance
            instance = pyblish.api.Instance(node.name())
            instance.data["family"] = "geometry"
            instance.data["families"] = ["writegeo"]
            instance.add(node)
            instance.data["label"] = node.name()
            instance.data["publish"] = False
            path, ext = os.path.splitext(nuke.filename(node))
            instance.data["output_path"] = "{0}_geometry{1}".format(path, ext)
            instances.append(instance)

        context.data["instances"] = (
            context.data.get("instances", []) + instances
        )


class CollectCacheProcess(pyblish.api.ContextPlugin):
    """Collect all local processing writegeo instances."""

    order = CollectWriteGeo.order + 0.01
    label = "Cache Local"
    hosts = ["nuke"]
    targets = ["process.local"]

    def process(self, context):
        import nuke

        formats = ["cache", "camera", "geometry"]
        for item in context.data["instances"]:
            families = [item.data["family"]] + item.data.get("families", [])
            # Skip any instances that is not valid.
            valid_families = set(formats)
            if len(valid_families & set(families)) != 1:
                continue

            fmt = list(valid_families & set(families))[0]

            instance = context.create_instance(item.data["name"])
            for key, value in item.data.iteritems():
                instance.data[key] = value

            instance.data["label"] += " - writegeo - local"
            instance.data["families"] = ["writegeo", "local"]
            for node in item:
                instance.add(node)

            # Adding/Checking publish attribute
            if "{0}_local".format(fmt) not in node.knobs():
                knob = nuke.Boolean_Knob(
                    "{0}_local".format(fmt), "{0} Local".format(fmt.title())
                )
                knob.setValue(False)
                node.addKnob(knob)

            value = bool(node["{0}_local".format(fmt)].getValue())

            # Compare against selection
            selection = instance.context.data.get("selection", [])
            if selection:
                if list(set(instance) & set(selection)):
                    value = True
                else:
                    value = False

            instance.data["publish"] = value

            if fmt == "cache":
                def instanceToggled(instance, value):
                    instance[0]["cache_local"].setValue(value)
                instance.data["instanceToggled"] = instanceToggled

            if fmt == "camera":
                def instanceToggled(instance, value):
                    instance[0]["camera_local"].setValue(value)
                instance.data["instanceToggled"] = instanceToggled

            if fmt == "geometry":
                def instanceToggled(instance, value):
                    instance[0]["geometry_local"].setValue(value)
                instance.data["instanceToggled"] = instanceToggled


class CollectCachePublish(pyblish.api.ContextPlugin):
    """Collect all local processing writegeo instances."""

    order = CollectWriteGeo.order + 0.01
    label = "Cache Local"
    hosts = ["nuke"]
    targets = ["default"]

    def process(self, context):
        import os
        import nuke

        formats = ["cache", "camera", "geometry"]
        for item in context.data["instances"]:
            families = [item.data["family"]] + item.data.get("families", [])
            # Skip any instances that is not valid.
            valid_families = set(formats)
            if len(valid_families & set(families)) != 1:
                continue

            # Skip instance if output does not exist
            if not os.path.exists(item.data["output_path"]):
                continue

            instance = context.create_instance(item.data["name"])
            for key, value in item.data.iteritems():
                instance.data[key] = value

            instance.data["label"] += (
                " - " + os.path.basename(instance.data["output_path"])
            )
            instance.data["families"] = ["writegeo"]
            for node in item:
                instance.add(node)

            fmt = list(valid_families & set(families))[0]

            # Adding/Checking publish attribute
            if "{0}_publish".format(fmt) not in node.knobs():
                knob = nuke.Boolean_Knob(
                    "{0}_publish".format(fmt),
                    "{0} Publish".format(fmt.title())
                )
                knob.setValue(False)
                node.addKnob(knob)

            value = bool(node["{0}_local".format(fmt)].getValue())

            # Compare against selection
            selection = instance.context.data.get("selection", [])
            if selection:
                if list(set(instance) & set(selection)):
                    value = True
                else:
                    value = False

            instance.data["publish"] = value

            if fmt == "cache":
                def instanceToggled(instance, value):
                    instance[0]["cache_publish"].setValue(value)
                instance.data["instanceToggled"] = instanceToggled

            if fmt == "camera":
                def instanceToggled(instance, value):
                    instance[0]["camera_publish"].setValue(value)
                instance.data["instanceToggled"] = instanceToggled

            if fmt == "geometry":
                def instanceToggled(instance, value):
                    instance[0]["geometry_publish"].setValue(value)
                instance.data["instanceToggled"] = instanceToggled
