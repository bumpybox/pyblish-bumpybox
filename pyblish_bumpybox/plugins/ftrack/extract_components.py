import pyblish.api


class BumpyboxFtrackExtractComponents(pyblish.api.InstancePlugin):
    """ Appending output files from local extraction as components. """

    order = pyblish.api.ExtractorOrder + 0.49
    label = "Components"
    families = ["local", "output"]

    def process(self, instance):

        paths = []

        if "collection" in instance.data:
            paths.append(instance.data["collection"].format())
        """
        if "collections" in instance.data:
            for collection in instance.data["collections"]:
                paths.append(collection.format())
        """
        if paths:
            for path in paths:
                components = instance.data.get("ftrackComponents", {})
                data = {"path": path, "overwrite": True}
                name = instance.data.get(
                    "component_name", instance.data["name"]
                )
                components[name] = data
                instance.data["ftrackComponents"] = components
