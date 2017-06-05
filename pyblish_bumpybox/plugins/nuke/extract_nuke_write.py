import os

import nuke
import pyblish.api


class ExtractNukeWrite(pyblish.api.InstancePlugin):
    """ Extract output from write nodes. """

    order = pyblish.api.ExtractorOrder
    optional = True
    families = ["write", "local"]
    label = "Write"
    hosts = ["nuke"]
    match = pyblish.api.Subset

    def process(self, instance):

        # Get frame range
        node = instance[0]
        first_frame = nuke.root()["first_frame"].value()
        last_frame = nuke.root()["last_frame"].value()

        if node["use_limit"].value():
            first_frame = node["first"].value()
            last_frame = node["last"].value()

        # Render frames
        nuke.execute(node.name(), int(first_frame), int(last_frame))

        # Validate output
        for filename in list(instance.data["collection"]):
            if not os.path.exists(filename):
                instance.data["collection"].remove(filename)
                self.log.warning("\"{0}\" didn't render.".format(filename))
