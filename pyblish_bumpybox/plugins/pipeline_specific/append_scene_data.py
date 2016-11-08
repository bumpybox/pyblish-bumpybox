import os

import pyblish.api


class AppendSceneData(pyblish.api.InstancePlugin):
    """ Appending data to scene instance """

    # offset to get instance from creation
    order = pyblish.api.CollectorOrder + 0.2

    def process(self, instance):

        current_file = instance.context.data("currentFile")
        current_dir = os.path.dirname(current_file)
        publish_dir = os.path.join(current_dir, "publish")
        publish_file = os.path.join(publish_dir,
                                    os.path.basename(current_file))

        instance.data["publishPath"] = publish_file

        # ftrack data
        if "ftrackComponents" in instance.data:
            host = pyblish.api.current_host()

            components = instance.data["ftrackComponents"]
            components["%s_publish" % host] = {"path": publish_file}
            instance.data["ftrackComponents"] = components

        self.log.info("something")


class testValidator(pyblish.api.InstancePlugin):

    order = pyblish.api.ValidatorOrder

    def process(self, instance):

        self.log.info(instance.data["publishPath"])
