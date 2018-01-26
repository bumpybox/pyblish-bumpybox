from pyblish import api
from pyblish_bumpybox import inventory


class CollectSets(api.ContextPlugin):
    """ Collects all sets in scene """

    order = inventory.get_order(__file__, "CollectSets")
    label = "Sets"
    hosts = ["maya"]
    targets = ["default", "process"]

    def validate_set(self, object_set):

        for member in object_set.members():
            if member.nodeType() in ["transform"]:
                return True

        return False

    def process(self, context):
        import os

        import pymel.core as pm

        instances = []
        for object_set in pm.ls(type="objectSet"):

            if object_set.nodeType() != "objectSet":
                continue

            if not self.validate_set(object_set):
                continue

            # Exclude specific sets
            invalid_sets = [
                "lightEditorRoot", "defaultLightSet", "defaultObjectSet"
            ]
            if object_set.name() in invalid_sets:
                continue

            extensions = {
                "mayaAscii": "ma", "mayaBinary": "mb", "alembic": "abc",
                "camera": "abc", "geometry": "abc"
            }
            family_mappings = {
                "mayaAscii": "scene", "mayaBinary": "scene",
                "alembic": "cache", "geometry": "geometry", "camera": "camera"
            }

            geometry = []
            cameras = []
            for member in object_set.members():
                try:
                    node_type = member.getShape().nodeType()
                except:
                    continue
                if node_type == "camera":
                    cameras.append(member)
                if node_type == "mesh":
                    geometry.append(member)

            # Add an instance per format supported.
            formats = [
                "mayaBinary", "mayaAscii", "alembic", "camera", "geometry"
            ]
            for fmt in formats:

                # Skip camera instances when there are no cameras in the set
                if fmt == "camera" and not cameras:
                    continue

                # Skip geometry instances when there are no geometry in the set
                if fmt == "geometry" and not geometry:
                    continue

                # Remove illegal disk characters
                name = object_set.name().replace(":", "_")

                name += "_" + fmt

                instance = plugin.Instance(name)
                instance.add(object_set)

                instance.data["nodes"] = object_set.members()
                if fmt == "camera":
                    instance.data["nodes"] = cameras
                if fmt == "geometry":
                    instance.data["nodes"] = geometry

                families = [fmt, family_mappings[fmt], "set"]
                instance.data["families"] = families
                instance.data["family"] = family_mappings[fmt]

                label = "{0} - {1}".format(name, fmt)
                instance.data["label"] = label

                # Adding/Checking publish attribute
                instance.data["publish"] = False
                if hasattr(object_set, fmt):
                    attr = pm.Attribute(object_set.name() + "." + fmt)
                    instance.data["publish"] = attr.get()
                else:
                    pm.addAttr(
                        object_set,
                        longName=fmt,
                        defaultValue=False,
                        attributeType="bool"
                    )
                    attr = pm.Attribute(object_set.name() + "." + fmt)
                    pm.setAttr(attr, channelBox=True)

                # Set output path
                filename = "{0}_{1}.{2}".format(
                    os.path.splitext(
                        os.path.basename(context.data["currentFile"])
                    )[0],
                    name,
                    extensions[fmt]
                )
                path = os.path.join(
                    os.path.dirname(context.data["currentFile"]),
                    "workspace", filename
                )
                instance.data["output_path"] = path

                def instance_toggled(instance, value):
                    node = instance[0]

                    families = instance.data.get("families", [])

                    attrs = []
                    for attr in node.listAttr(userDefined=True):
                        attrs.append(attr.name(includeNode=False))

                    attr_list = list(set(attrs) & set(families))

                    if attr_list:
                        node.attr(attr_list[0]).set(value)
                instance.data["instanceToggled"] = instance_toggled

                instances.append(instance)

        context.data["instances"] = (
            context.data.get("instances", []) + instances
        )


class CollectSetsLocal(api.ContextPlugin):
    """Collect all local processing write instances."""

    order = inventory.get_order(__file__, "CollectSetsLocal")
    label = "Sets Local"
    hosts = ["maya"]
    targets = ["process.local"]

    def process(self, context):

        for item in context.data["instances"]:
            # Skip any instances that is not valid.
            valid_families = [
                "alembic", "mayaAscii", "mayaBinary", "camera", "geometry"
            ]
            if len(set(valid_families) & set(item.data["families"])) != 1:
                continue

            instance = context.create_instance(item.data["name"])
            for key, value in item.data.iteritems():
                instance.data[key] = value

            instance.data["families"] += ["local"]
            for node in item:
                instance.add(node)
