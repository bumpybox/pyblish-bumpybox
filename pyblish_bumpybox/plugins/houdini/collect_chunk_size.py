import hou

import pyblish.api


class BumpyboxHoudiniCollectChunkSize(pyblish.api.InstancePlugin):

    order = pyblish.api.CollectorOrder + 0.1
    families = ["farm"]
    label = "Chunk Size"

    def process(self, instance):

        node = instance[0]
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
