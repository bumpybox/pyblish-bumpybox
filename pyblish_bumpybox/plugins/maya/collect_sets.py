import os

import pyblish.api
import pymel.core
import clique


class BumpyboxMayaCollectSets(pyblish.api.ContextPlugin):
    """ Collects all sets in scene """

    order = pyblish.api.CollectorOrder
    label = "Sets"
    hosts = ["maya"]

    def transform_set(self, object_set):
        if not object_set.members():
            return False

        for member in object_set.members():
            if (member.nodeType() != "transform" and
               member.nodeType() != "objectSet"):
                return False

        return True

    def process(self, context):

        for object_set in pymel.core.ls(type="objectSet"):

            if not self.transform_set(object_set):
                continue

            extensions = {
                "mayaAscii": "ma", "mayaBinary": "mb", "alembic": "abc"
            }
            family_mappings = {
                "mayaAscii": "scene", "mayaBinary": "scene", "alembic": "cache"
            }

            # Checking instance type. If object has attribute "remote" set to
            # true, its considered a "remote" instance.
            instance_type = "local"
            if hasattr(object_set, "remote"):
                attr = pymel.core.Attribute(object_set.name() + ".remote")
                if attr.get():
                    instance_type = "remote"
                    # Remote cache/formats are currently disabled as no
                    # remotes (Deadline) submission are setup to handle them.
                    continue
            else:
                pymel.core.addAttr(object_set,
                                   longName="remote",
                                   defaultValue=False,
                                   attributeType="bool")
                attr = pymel.core.Attribute(object_set.name() + ".remote")
                pymel.core.setAttr(attr, channelBox=True)

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
                    attr = pymel.core.Attribute(object_set.name() + "." + fmt)
                    instance.data["publish"] = attr.get()
                else:
                    pymel.core.addAttr(object_set,
                                       longName=fmt,
                                       defaultValue=False,
                                       attributeType="bool")
                    attr = pymel.core.Attribute(object_set.name() + "." + fmt)
                    pymel.core.setAttr(attr, channelBox=True)

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
                    pymel.core.playbackOptions(query=True, minTime=True)
                )
                collection.add(head + str(frame_start).zfill(4) + tail)

                instance.data["collection"] = collection
