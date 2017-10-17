import os

import pyblish.api
import pymel.core as pm


class CollectMayaSets(pyblish.api.ContextPlugin):
    """ Collects all sets in scene """

    order = pyblish.api.CollectorOrder
    label = "Sets"
    hosts = ["maya"]
    targets = ["default", "process"]

    def validate_set(self, object_set):

        for member in object_set.members():
            if member.nodeType() in ["transform"]:
                return True

        return False

    def process(self, context):

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
                "mayaAscii": "ma", "mayaBinary": "mb", "alembic": "abc"
            }
            family_mappings = {
                "mayaAscii": "scene", "mayaBinary": "scene", "alembic": "cache"
            }

            # Add an instance per format supported.
            for fmt in ["mayaBinary", "mayaAscii", "alembic"]:

                # Remove illegal disk characters
                name = object_set.name().replace(":", "_")

                # Because mayaAscii and mayaBinary share the same family, we'll
                # need to make the names different to avoid overwriting based
                # on the name alone.
                if fmt != "alembic":
                    name += "_" + fmt

                instance = pyblish.api.Instance(name)
                instance.add(object_set)

                families = [fmt, family_mappings[fmt]]
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

                instances.append(instance)

        context.data["instances"] = (
            context.data.get("instances", []) + instances
        )


class CollectMayaSetsLocal(pyblish.api.ContextPlugin):
    """Collect all local processing write instances."""

    order = CollectMayaSets.order + 0.01
    label = "Sets Local"
    hosts = ["maya"]
    targets = ["process.local"]

    def process(self, context):

        for item in context.data["instances"]:
            # Skip any instances that is not valid.
            valid_families = ["alembic", "mayaAscii", "mayaBinary"]
            if len(set(valid_families) & set(item.data["families"])) != 1:
                continue

            instance = context.create_instance(item.data["name"])
            for key, value in item.data.iteritems():
                instance.data[key] = value

            instance.data["families"] += ["local"]
            for node in item:
                instance.add(node)
