import pyblish.api
import ftrack_locations


class ExtractFtrackComponents(pyblish.api.InstancePlugin):
    """ Appending output files from local extraction as components. """

    order = pyblish.api.ExtractorOrder + 0.4
    label = "Components"
    families = ["local", "output"]

    def process(self, instance):

        if not instance.data["publish"]:
            return

        if "collection" in instance.data:

            # Add component
            families = instance.data.get("families", [])
            valid_families = ["img", "scene", "cache", "mov"]

            self.add_ftrack_components(
                instance,
                list(set(families) & set(valid_families))[0],
                instance.data["collection"].format()
            )

        if "gizmo" in instance.data["families"]:

            self.add_ftrack_components(
                instance,
                "nuke_gizmo",
                instance.data["outputPath"]
            )

        if "lut" in instance.data["families"]:

            instance.data["component_name"] = "main"
            self.add_ftrack_components(
                instance,
                "lut",
                instance.data["outputPath"]
            )

    def add_ftrack_components(self, instance, assettype_short, component_path):

        components = instance.data.get("ftrackComponentsList", [])
        components.append({
            "assettype_data": {"short": assettype_short},
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
        })
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
