import pyblish.api
from ftrack_locations import ftrack_template_disk


class BumpyboxFtrackExtractComponents(pyblish.api.InstancePlugin):
    """ Appending output files from local extraction as components. """

    order = pyblish.api.ExtractorOrder + 0.4
    label = "Components"
    families = ["local", "output"]

    def process(self, instance):

        if "collection" in instance.data:

            # Add ftrack family
            families = instance.data.get("families", [])
            instance.data["families"] = families + ["ftrack"]

            # Add component
            valid_families = ["img", "scene", "cache", "mov"]

            components = instance.data.get("ftrackComponentsList", [])
            components.append({
                "assettype_data": {
                    "short": list(set(families) & set(valid_families))[0]
                },
                "assetversion_data": {
                    "version": instance.context.data["version"]
                },
                "component_data": {
                    "name": instance.data.get(
                        "component_name", instance.data["name"]
                    ),
                },
                "component_path": instance.data["collection"].format(),
                "component_overwrite": True,
            })
            instance.data["ftrackComponentsList"] = components


class BumpyboxFtrackExtractLocation(pyblish.api.InstancePlugin):
    """ Appending output files from local extraction as components. """

    order = BumpyboxFtrackExtractComponents.order + 0.01
    label = "Location"
    families = ["local", "output"]

    def process(self, instance):

        # Setup location
        session = instance.context.data["ftrackSession"]
        location = ftrack_template_disk.get_new_location(session)

        for data in instance.data.get("ftrackComponentsList", []):
            data["component_location"] = location
