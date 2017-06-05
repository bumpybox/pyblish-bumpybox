import os

import pyblish.api
import clique


class IntegrateFtrackCleanUp(pyblish.api.InstancePlugin):
    """ Clean up any workspace files that has been integrated.

    Offset to get component from pyblish-ftrack
    """

    order = pyblish.api.IntegratorOrder + 0.1
    label = "Ftrack Clean Up"
    families = ["ftrack"]
    optional = True

    def process(self, instance):

        for data in instance.data.get("ftrackComponentsList", []):
            path = data["component_path"]
            if "component" in data and "workspace" in path:

                try:
                    collection = clique.parse(path)
                    for f in collection:
                        os.remove(f)
                        self.log.info("Deleted: \"{0}\"".format(f))
                except:
                    os.remove(path)
                    self.log.info("Deleted: \"{0}\"".format(path))
