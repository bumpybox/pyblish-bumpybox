import os

import pyblish.api


class BumpyboxHoudiniExtractLocal(pyblish.api.InstancePlugin):
    """ Extracts nodes locally. """

    families = ["mantra", "alembic", "dynamics", "geometry"]
    order = pyblish.api.ExtractorOrder
    label = "Local"
    optional = True

    def process(self, instance):

        node = instance[0]

        node.parm("execute").pressButton()

        # raising any errors
        if node.errors():
            raise ValueError(node.errors())

        # gather extracted files
        collection = instance.data["collection"]
        for f in collection:
            if not os.path.exists(f):
                collection.remove(f)
