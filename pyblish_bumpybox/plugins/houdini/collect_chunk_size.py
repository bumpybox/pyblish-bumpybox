import hou

import pyblish.api


class BumpyboxHoudiniCollectChunkSize(pyblish.api.ContextPlugin):
    """ Add remoteChunkSize to remote instances.

    A ContextPlugin because if remote instance is unpublishable,
    it won't activate the processing.
    """

    order = pyblish.api.CollectorOrder + 0.1
    label = "Chunk Size"
    hosts = ["houdini"]

    def process(self, context):

        for instance in context:

            # Filter to remote instances only
            if "remote" not in instance.data.get("families", []):
                continue

            node = instance[0]
            instance.data["remoteChunkSize"] = 1
            try:
                chunk_size = node.parm("remoteChunkSize").eval()
                instance.data["remoteChunkSize"] = chunk_size
            except:
                parm_group = node.parmTemplateGroup()
                parm_folder = hou.FolderParmTemplate("folder", "Extras")
                parm_template = hou.IntParmTemplate("remoteChunkSize",
                                                    "Remote Chunk Size", 1)
                parm_folder.addParmTemplate(parm_template)
                parm_group.append(parm_folder)
                node.setParmTemplateGroup(parm_group)
                node.parm("remoteChunkSize").set(1)
                msg = "No existing \"remoteChunkSize\" parameter."
                msg += " Adding default parameter of 1."
                self.log.info(msg)
