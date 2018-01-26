from pyblish_bumpybox import plugin


class ExtractComponents(plugin.InstancePlugin):
    """Appending output files from local extraction as components.

    This plugin generates component data from either the instance data or
    defaults. Finding "collection" or "output_path" in the instance data
    trigger the component data generation.
    """

    order = plugin.ExtractorOrder + 0.4
    label = "Components"
    families = ["local", "output"]

    def process(self, instance):

        if "collection" in instance.data:
            self.add_ftrack_components(
                instance,
                instance.data["collection"].format(
                    pattern=instance.data.get(
                        "pattern", "{head}{padding}{tail} [{ranges}]"
                    )
                )
            )

        if "output_path" in instance.data:
            self.add_ftrack_components(
                instance,
                instance.data["output_path"]
            )

    def add_ftrack_components(self, instance, component_path):

        component = {
            "assettype_data": {},
            "asset_data": {},
            "component_metadata": instance.data.get("component_metadata", {}),
            "component_path": component_path,
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

        if "component_overwrite" in instance.data.keys():
            component["component_overwrite"] = instance.data[
                "component_overwrite"
            ]

        if "component_location" in instance.data.keys():
            component["component_location"] = instance.data[
                "component_location"
            ]

        components = instance.data.get("ftrackComponentsList", [])
        components.append(component)
        instance.data["ftrackComponentsList"] = components


class ExtractGizmo(plugin.InstancePlugin):
    """Sets the data for Ftrack gizmo component."""

    order = plugin.ExtractorOrder
    label = "Ftrack Gizmo"
    families = ["gizmo"]

    def process(self, instance):

        data = instance.data.get("assettype_data", {})
        data.update({"short": "nuke_gizmo"})
        instance.data["assettype_data"] = data


class ExtractLUT(plugin.InstancePlugin):
    """Sets the data for Ftrack lut component."""

    order = plugin.ExtractorOrder
    label = "Ftrack LUT"
    families = ["lut"]

    def process(self, instance):

        data = instance.data.get("component_data", {})
        data.update({"name": "main"})
        instance.data["component_data"] = data

        data = instance.data.get("assettype_data", {})
        data.update({"short": "lut"})
        instance.data["assettype_data"] = data


class ExtractMovie(plugin.InstancePlugin):
    """Sets the data for Ftrack mov component."""

    order = plugin.ExtractorOrder
    label = "Ftrack Movie"
    families = ["mov"]

    def process(self, instance):

        data = instance.data.get("assettype_data", {})
        data.update({"short": "mov"})
        instance.data["assettype_data"] = data


class ExtractScene(plugin.InstancePlugin):
    """Sets the data for Ftrack scene component."""

    order = plugin.ExtractorOrder
    label = "Ftrack Scene"
    families = ["scene"]

    def process(self, instance):

        data = instance.data.get("assettype_data", {})
        data.update({"short": "scene"})
        instance.data["assettype_data"] = data


class ExtractImg(plugin.InstancePlugin):
    """Sets the data for Ftrack img component."""

    order = plugin.ExtractorOrder
    label = "Ftrack Img"
    families = ["img"]

    def process(self, instance):

        data = instance.data.get("assettype_data", {})
        data.update({"short": "img"})
        instance.data["assettype_data"] = data


class ExtractCache(plugin.InstancePlugin):
    """Sets the data for Ftrack cache component."""

    order = plugin.ExtractorOrder
    label = "Ftrack Cache"
    families = ["cache"]

    def process(self, instance):

        data = instance.data.get("assettype_data", {})
        data.update({"short": "cache"})
        instance.data["assettype_data"] = data


class ExtractCamera(plugin.InstancePlugin):
    """Sets the data for Ftrack camera component."""

    order = plugin.ExtractorOrder
    label = "Ftrack Camera"
    families = ["camera"]

    def process(self, instance):

        data = instance.data.get("assettype_data", {})
        data.update({"short": "camera"})
        instance.data["assettype_data"] = data


class ExtractGeometry(plugin.InstancePlugin):
    """Sets the data for Ftrack camera component."""

    order = plugin.ExtractorOrder
    label = "Ftrack Geometry"
    families = ["geometry"]

    def process(self, instance):

        data = instance.data.get("assettype_data", {})
        data.update({"short": "geometry"})
        instance.data["assettype_data"] = data
