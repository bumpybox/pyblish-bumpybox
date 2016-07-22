import re

import hou
import pyblish.api


class CollectGeometry(pyblish.api.ContextPlugin):
    """ Collects all geometry nodes """

    order = pyblish.api.CollectorOrder

    def process(self, context):

        node_type = hou.nodeType(hou.ropNodeTypeCategory(), 'geometry')
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

            instance = context.create_instance(name=node.name())
            instance.data["publish"] = not node.isBypassed()
            instance.add(node)

            # converting houdini frame padding to python padding
            # output paths are validated to "$F4", so its safe to replace
            path = node.parm("sopoutput").unexpandedString()
            instance.data["originalOutputPath"] = path

            path = node.parm("sopoutput").eval()
            instance.data["outputPath"] = re.sub(r"\.[0-9]{4}\.", ".%04d.",
                                                 path)

            # assigning families
            if node in nodes_local:
                instance.data["family"] = "cache.local.geometry"
                instance.data["families"] = ["cache.*", "cache.local.*"]
            else:
                instance.data["family"] = "cache.farm.geometry"
                instance.data["families"] = ["cache.*", "cache.farm.*",
                                             "deadline"]
