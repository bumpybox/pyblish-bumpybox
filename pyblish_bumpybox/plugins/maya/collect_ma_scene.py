import os

import pyblish.api


class CollectMaScene(pyblish.api.ContextPlugin):
    """ Collects the scene in ma format """

    order = pyblish.api.CollectorOrder

    def process(self, context):

        file_path = context.data["currentFile"].replace(".mb", ".ma")

        instance = context.create_instance(name=os.path.basename(file_path))
        instance.data["family"] = "scene.ma"
