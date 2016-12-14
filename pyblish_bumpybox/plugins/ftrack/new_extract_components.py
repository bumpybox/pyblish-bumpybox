import os

import pyblish.api
import ftrack_api
import ftrack_template


class Structure(ftrack_api.structure.base.Structure):

    def get_resource_identifier(self, entity, context=None):

        templates = ftrack_template.discover_templates()

        path = ftrack_template.format(
            {}, templates, entity=entity
        )[0].replace("\\", "/").replace("//", "/")

        if entity.entity_type == "SequenceComponent":

            padding = entity["padding"]
            if padding:
                expression = "%0{0}d".format(padding)
            else:
                expression = "%d"

            filetype = entity["file_type"]
            path = path.replace(
                filetype, "/{0}.{1}{2}".format(
                    os.path.splitext(os.path.basename(path))[0],
                    expression,
                    filetype
                )
            )

        return path


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
        location = session.ensure(
            "Location", {"name": "project.disk.root"}
        )
        location.structure = Structure()
        location.accessor = ftrack_api.accessor.disk.DiskAccessor(prefix="")

        for data in instance.data.get("ftrackComponentsList", []):
            data["component_location"] = location
