import pyblish.api


class BumpyboxFtrackExtractComponents(pyblish.api.InstancePlugin):
    """ Appending output files from local extraction as components. """

    order = pyblish.api.ExtractorOrder + 0.49
    label = "Components"
    families = ["local", "output"]

    def process(self, instance):

        if "collection" in instance.data:
            components = instance.data.get("ftrackComponents", {})
            data = {"path": instance.data["collection"].format(),
                    "overwrite": True}
            name = instance.data.get("component_name", instance.data["name"])
            components[name] = data
            instance.data["ftrackComponents"] = components
