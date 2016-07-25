import os
import re

import hou
import pyblish.api


class CollectMantra(pyblish.api.ContextPlugin):
    """ Collects all mantra nodes """

    order = pyblish.api.CollectorOrder

    def process(self, context):

        # storing plugin data
        node_type = hou.nodeType("Driver/ifd")
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
            # output paths are validated to 4 digit padding
            regex = re.compile(r"\.[0-9]{4}\.")

            soho_diskfile = node.parm("soho_diskfile").eval()
            soho_diskfile = regex.sub(".%04d.", soho_diskfile)

            vm_picture = node.parm("vm_picture").eval()
            vm_picture = regex.sub(".%04d.", vm_picture)

            # assigning families
            if node.parm("soho_outputmode").eval():
                instance.data["outputPath"] = soho_diskfile
                path = node.parm("soho_diskfile").unexpandedString()
                instance.data["originalOutputPath"] = path
                instance.data["renderOutputPath"] = vm_picture

                if node in nodes_local:
                    instance.data["family"] = "img.local.ifd"
                    instance.data["families"] = ["img.*", "img.local.*"]
                else:
                    instance.data["family"] = "img.farm.ifd"
                    instance.data["families"] = ["img.*", "img.farm.*",
                                                 "deadline"]
            else:
                instance.data["outputPath"] = vm_picture

                path = node.parm("vm_picture").unexpandedString()
                instance.data["originalOutputPath"] = path

                ext = os.path.splitext(vm_picture)[1][1:]
                if node in nodes_local:
                    instance.data["family"] = "img.local." + ext
                    instance.data["families"] = ["img.*", "img.local.*"]
                else:
                    instance.data["family"] = "img.farm." + ext
                    instance.data["families"] = ["img.*", "img.farm.*",
                                                 "deadline"]
