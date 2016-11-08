import os

import pyblish.api


class CollectScene(pyblish.api.ContextPlugin):
    """ Collecting the scene from the context """

    # offset to get latest currentFile from context
    order = pyblish.api.CollectorOrder + 0.1

    def process(self, context):

        current_file = context.data("currentFile")

        # create instance
        instance = context.create_instance(name=os.path.basename(current_file))

        instance.data["family"] = "scene"
        instance.data["path"] = current_file

        # ftrack data
        if "ftrackData" not in instance.context.data:
            return

        instance.data["ftrackAssetType"] = "scene"

        ftrack_data = instance.context.data("ftrackData")
        instance.data["ftrackAssetName"] = ftrack_data["Task"]["name"]

        component_name = "%s_work" % pyblish.api.current_host()
        components = {component_name: {"path": current_file}}
        instance.data["ftrackComponents"] = components
