import os

import pyblish.api
import pymel.core as pm
import clique


class BumpyboxMayaCollectSets(pyblish.api.ContextPlugin):
    """ Collects all sets in scene """

    order = pyblish.api.CollectorOrder
    label = "Sets"
    hosts = ["maya"]

    def validate_set(self, object_set):

        for member in object_set.members():
            if member.nodeType() in ["transform"]:
                return True

        return False

    def process(self, context):

        # Collect sets named starting with "remote".
        remote_members = []
        for object_set in pm.ls(type="objectSet"):

            if object_set.name().lower().startswith("remote"):
                remote_members.extend(object_set.members())

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

            # Checking instance type.
            instance_type = "local"
            if object_set in remote_members:
                instance_type = "remote"

            # Add an instance per format supported.
            for fmt in ["mayaBinary", "mayaAscii", "alembic"]:

                # Remove illegal disk characters
                name = object_set.name().replace(":", "_")

                instance = context.create_instance(name=name)
                instance.add(object_set)

                families = [fmt, family_mappings[fmt], instance_type]
                instance.data["families"] = families

                label = "{0} - {1} - {2}".format(name, fmt, instance_type)
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

                # Generate collection
                filename = os.path.splitext(
                    os.path.basename(context.data["currentFile"])
                )[0]
                path = os.path.join(
                    os.path.dirname(context.data["currentFile"]),
                    "workspace", filename
                )
                head = "{0}_{1}.".format(path, name)
                tail = "." + extensions[fmt]
                collection = clique.Collection(head=head, padding=4, tail=tail)

                frame_start = int(
                    pm.playbackOptions(query=True, minTime=True)
                )
                collection.add(head + str(frame_start).zfill(4) + tail)

                instance.data["collection"] = collection
