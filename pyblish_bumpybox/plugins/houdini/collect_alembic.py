import hou
import pyblish.api


class CollectAlembic(pyblish.api.ContextPlugin):
    """ Collects all alembic nodes """

    order = pyblish.api.CollectorOrder

    def process(self, context):

        # storing plugin data
        node_type = hou.nodeType(hou.ropNodeTypeCategory(), "alembic")
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

            instance.data["outputPath"] = node.parm("filename").eval()

            path = node.parm("filename").unexpandedString()
            instance.data["originalOutputPath"] = path

            if node in nodes_local:
                instance.data["family"] = "cache.local.abc"
                instance.data["families"] = ["cache.*", "cache.local.*"]
            else:
                instance.data["family"] = "cache.farm.abc"
                instance.data["families"] = ["cache.*", "cache.farm.*",
                                             "deadline"]
