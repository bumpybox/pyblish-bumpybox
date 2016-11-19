import os

import hou

import pyblish.api
import clique


class BumpyboxDeadlineCollectHoudiniRender(pyblish.api.InstancePlugin):
    """ Append render output path to instances. """

    order = pyblish.api.CollectorOrder + 0.4
    families = ["render"]
    label = "Houdini Render"

    def process(self, instance):

        node = instance[0]

        # Get expected output files.
        files = []
        if node.parm("trange").eval() == 0:
            frame = int(hou.frame())
            files.append(node.parm("vm_picture").evalAtFrame(frame))
        else:
            start = node.parm("f1").eval()
            end = node.parm("f2").eval()
            step = node.parm("f3").eval()
            for frame in range(int(start), int(end) + 1, int(step)):
                files.append(node.parm("vm_picture").evalAtFrame(frame))

        # Get extension
        ext = os.path.splitext(files[0])[1]

        # Create output collection.
        collections = clique.assemble(files, minimum_items=1)[0]
        collection = None
        for col in collections:
            if col.format("{tail}") == ext:
                collection = col

        if collection:
            instance.data["render"] = collection.format()
