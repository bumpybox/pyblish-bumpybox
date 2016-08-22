import os
import re

import hou
import pyblish.api


class CollectDynamics(pyblish.api.ContextPlugin):
    """ Collects all dynamics nodes """

    order = pyblish.api.CollectorOrder

    def process(self, context):

        node_type = hou.nodeType(hou.ropNodeTypeCategory(), "dop")
        nodes = node_type.instances()

        # categorize nodes based on whether they are in a network box starting
        # with "farm"
        nodes_local = list(nodes)
        for box in hou.node("out").networkBoxes():
            if box.name().startswith("farm"):
                for node in box.nodes():
                    if node in nodes_local:
                        nodes_local.remove(node)

        # creating instances per mantra node
        for node in nodes:

            # currently not developed pipeline for distributed simulations
            if node not in nodes_local:
                continue

            instance = context.create_instance(name=node.name())
            instance.data["publish"] = not node.isBypassed()
            instance.add(node)

            # collet frame padding
            frame_padding = 4
            end_frame = int(hou.hscriptExpression("$FEND"))
            if len(str(int(end_frame))) > 4:
                frame_padding = len(str(int(end_frame)))

            instance.data["framePadding"] = frame_padding

            # converting houdini frame padding to python padding
            # output paths are validated to "$F4", so its safe to replace
            path = node.parm("dopoutput").unexpandedString()
            instance.data["originalOutputPath"] = path

            path = node.parm("dopoutput").eval()
            padding_string = ".%{0}d.".format(str(frame_padding).zfill(2))
            instance.data["outputPath"] = re.sub(".-001.", padding_string,
                                                 path)

            ext = os.path.splitext(path)[1]

            # assigning families
            if node in nodes_local:
                instance.data["family"] = "cache.local" + ext
                instance.data["families"] = ["cache.*", "cache.local.*"]
            else:
                instance.data["family"] = "cache.farm" + ext
                instance.data["families"] = ["cache.*", "cache.farm.*",
                                             "deadline"]
