import pyblish.api


class ExtractFtrackComponents(pyblish.api.InstancePlugin):
    """Appending output files from local extraction as components.

    This plugin generates component data from either the instance data or
    defaults. Finding "collection" or "output_path" in the instance data
    trigger the component data generation.
    """

    order = pyblish.api.ExtractorOrder + 0.4
    label = "Components"
    families = ["local", "output"]

    def process(self, instance):

        if not instance.data.get("publish", True):
            return

        if "collection" in instance.data:
            self.add_ftrack_components(
                instance,
                instance.data["collection"].format()
            )

        if "output_path" in instance.data:
            self.add_ftrack_components(
                instance,
                instance.data["output_path"]
            )

    def add_ftrack_components(self, instance, component_path):

        component = {
            "component_metadata": instance.data.get("component_metadata", {}),
            "component_path": component_path,
            "component_overwrite": instance.data.get(
                "component_overwrite", True
            ),
            "component_location": instance.data.get(
                "component_location",
                instance.context.data["ftrackSession"].pick_location()
            )
        }

        component["assettype_data"].update(
            instance.data.get("assettype_data", {})
        )
        component["asset_data"].update(
            instance.data.get("asset_data", {})
        )

        data = instance.data.get("assetversion_data", {})
        if "version" not in data.keys():
            data["version"] = instance.data.get(
                "version", instance.context.data["version"]
            )
        component["assetversion_data"] = data

        data = instance.data.get("component_data", {})
        if "name" not in data.keys():
            data["name"] = instance.data["name"]
        component["component_data"] = data

        components = instance.data.get("ftrackComponentsList", [])
        components.append(component)
        instance.data["ftrackComponentsList"] = components


class ExtractFtrackGizmo(pyblish.api.InstancePlugin):
    """Sets the data for Ftrack gizmo component."""

    order = pyblish.api.ExtractorOrder
    label = "Ftrack Gizmo"
    families = ["gizmo"]

    def process(self, instance):

        data = instance.data.get("assettype_data", {})
        data.update({"short": "nuke_gizmo"})
        instance.data["assettype_data"] = data


class ExtractFtrackLUT(pyblish.api.InstancePlugin):
    """Sets the data for Ftrack lut component."""

    order = pyblish.api.ExtractorOrder
    label = "Ftrack LUT"
    families = ["lut"]

    def process(self, instance):

        data = instance.data.get("component_data", {})
        data.update({"name": "main"})
        instance.data["component_data"] = data

        data = instance.data.get("assettype_data", {})
        data.update({"short": "lut"})
        instance.data["assettype_data"] = data


class ExtractFtrackMovie(pyblish.api.InstancePlugin):
    """Sets the data for Ftrack mov component."""

    order = pyblish.api.ExtractorOrder
    label = "Ftrack Movie"
    families = ["mov"]

    def process(self, instance):

        data = instance.data.get("assettype_data", {})
        data.update({"short": "mov"})
        instance.data["assettype_data"] = data


class ExtractFtrackScene(pyblish.api.InstancePlugin):
    """Sets the data for Ftrack scene component."""

    order = pyblish.api.ExtractorOrder
    label = "Ftrack Scene"
    families = ["scene"]

    def process(self, instance):

        data = instance.data.get("assettype_data", {})
        data.update({"short": "scene"})
        instance.data["assettype_data"] = data


class ExtractFtrackImg(pyblish.api.InstancePlugin):
    """Sets the data for Ftrack img component."""

    order = pyblish.api.ExtractorOrder
    label = "Ftrack Img"
    families = ["img"]

    def process(self, instance):

        data = instance.data.get("assettype_data", {})
        data.update({"short": "img"})
        instance.data["assettype_data"] = data


class ExtractFtrackCache(pyblish.api.InstancePlugin):
    """Sets the data for Ftrack cache component."""

    order = pyblish.api.ExtractorOrder
    label = "Ftrack Cache"
    families = ["cache"]

    def process(self, instance):

        data = instance.data.get("assettype_data", {})
        data.update({"short": "cache"})
        instance.data["assettype_data"] = data
