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

            # Add component
            families = instance.data.get("families", [])
            valid_families = ["img", "scene", "cache", "mov"]

            instance.data["assettype_short"] = list(
                set(families) & set(valid_families)
            )[0]

            self.add_ftrack_components(
                instance,
                instance.data["collection"].format()
            )

        if "output_path" in instance.data:

            # Add component
            families = instance.data.get("families", [])
            valid_families = ["gizmo", "lut", "scene"]

            instance.data["assettype_short"] = list(
                set(families) & set(valid_families)
            )[0]

            self.add_ftrack_components(
                instance,
                instance.data["output_path"]
            )

    def add_ftrack_components(self, instance, component_path):

        component = {
            "assettype_data": {
                "short": instance.data.get("assettype_short", "upload")
            },
            "asset_data": {
                "name": instance.data.get(
                    "asset_name",
                    instance.context.data["ftrackTask"]["name"]
                ),
                "parent": instance.data.get(
                    "asset_parent",
                    instance.context.data["ftrackTask"]["parent"]
                )
            },
            "assetversion_data": {
                "version": instance.data.get(
                    "version", instance.context.data["version"]
                )
            },
            "component_data": {
                "name": instance.data.get(
                    "component_name", instance.data["name"]
                ),
            },
            "component_path": component_path,
            "component_overwrite": instance.data.get(
                "component_overwrite", True
            ),
            "component_location": instance.data.get("component_location", None)
        }

        # Remove component location key if no location was found. This is done
        # so the session location can be picked up when integrating.
        if "component_location" not in instance.data:
            del component["component_location"]

        components = instance.data.get("ftrackComponentsList", [])
        components.append(component)
        instance.data["ftrackComponentsList"] = components
