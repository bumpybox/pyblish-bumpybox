import pyblish.api
import ftrack_locations


class ExtractFtrackComponents(pyblish.api.InstancePlugin):
    """Appending output files from local extraction as components.

    This plugin generates component data from either the instance data or
    defaults. Finding "collection" or "output" in the instance data trigger the
    component data generation.
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

        if "output" in instance.data:

            # Add component
            families = instance.data.get("families", [])
            valid_families = ["gizmo", "lut"]

            self.add_ftrack_components(
                instance,
                instance.data["output"]
            )

    def add_ftrack_components(self, instance, component_path):

        components = instance.data.get("ftrackComponentsList", [])
        components.append(
            {
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
                "component_overwrite": True,
            }
        )
        instance.data["ftrackComponentsList"] = components


class BumpyboxFtrackExtractLocation(pyblish.api.InstancePlugin):
    """ Appending output files from local extraction as components. """

    order = ExtractFtrackComponents.order + 0.01
    label = "Location"
    families = ["local", "output"]

    def process(self, instance):

        # Setup location
        session = instance.context.data["ftrackSession"]
        location = ftrack_locations.get_new_location(session)

        for data in instance.data.get("ftrackComponentsList", []):
            data["component_location"] = location
