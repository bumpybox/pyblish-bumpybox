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

            # collet frame padding
            frame_padding = 4
            end_frame = int(hou.hscriptExpression("$FEND"))
            if len(str(int(end_frame))) > 4:
                frame_padding = len(str(int(end_frame)))

            instance.data["framePadding"] = frame_padding

            # converting houdini frame padding to python padding
            # output paths are validated to 4 digit padding
            regex = re.compile(r"\.[0-9]{4,}\.")
            python_padding = ".%{0}d.".format(str(frame_padding).zfill(2))

            soho_diskfile = node.parm("soho_diskfile").eval()
            soho_diskfile = regex.sub(python_padding, soho_diskfile)

            vm_picture = node.parm("vm_picture").eval()
            vm_picture = regex.sub(python_padding, vm_picture)

            # getting deep output
            instance.data["deepPath"] = ""
            if node.parm("vm_deepresolver").eval() == "shadow":
                path = node.parm("vm_dsmfilename").unexpandedString()
                instance.data["deepPath"] = path
            if node.parm("vm_deepresolver").eval() == "camera":
                path = node.parm("vm_dcmfilename").unexpandedString()
                instance.data["deepPath"] = path

            # assigning families
            family_name = "img."
            if node in nodes_local:
                family_name += "local."
                instance.data["families"] = ["img.*", "img.local.*"]
            else:
                family_name += "farm."
                instance.data["families"] = ["img.*", "img.farm.*",
                                             "deadline"]

                # collecting chunk size
                instance.data["farmChunkSize"] = 1
                try:
                    chunk_size = node.parm("farmChunkSize").eval()
                    instance.data["farmChunkSize"] = chunk_size
                except:
                    parm_group = node.parmTemplateGroup()
                    parm_folder = hou.FolderParmTemplate("folder", "Extras")
                    parm_template = hou.IntParmTemplate("farmChunkSize",
                                                        "Farm Chunk Size", 1)
                    parm_folder.addParmTemplate(parm_template)
                    parm_group.append(parm_folder)
                    node.setParmTemplateGroup(parm_group)
                    node.parm("farmChunkSize").set(1)
                    msg = "No existing \"farmChunkSize\" parameter."
                    msg += " Adding default parameter of 1."
                    self.log.info(msg)

            # assigning families
            if node.parm("soho_outputmode").eval():
                instance.data["outputPath"] = soho_diskfile
                path = node.parm("soho_diskfile").unexpandedString()
                instance.data["originalOutputPath"] = path
                instance.data["renderOutputPath"] = vm_picture
                instance.data["family"] = family_name + "ifd"
            else:
                instance.data["outputPath"] = vm_picture

                path = node.parm("vm_picture").unexpandedString()
                instance.data["originalOutputPath"] = path

                ext = os.path.splitext(vm_picture)[1][1:]
                instance.data["family"] = family_name + ext
