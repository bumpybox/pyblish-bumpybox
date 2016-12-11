import os
import platform

import pyblish.api
import ftrack_api


class StandardStructure(ftrack_api.structure.standard.StandardStructure):

    def _get_parts(self, entity):
        '''Return resource identifier parts from *entity*.'''
        session = entity.session

        version = entity['version']

        if version is ftrack_api.symbol.NOT_SET and entity['version_id']:
            version = session.get('AssetVersion', entity['version_id'])

        error_message = (
            'Component {0!r} must be attached to a committed '
            'version and a committed asset with a parent context.'.format(
                entity
            )
        )

        if (
            version is ftrack_api.symbol.NOT_SET or
            version in session.created
        ):
            raise ftrack_api.exception.StructureError(error_message)

        link = version['link']

        if not link:
            raise ftrack_api.exception.StructureError(error_message)

        structure_names = [
            item['name']
            for item in link[1:-1]
        ]

        project_id = link[0]['id']
        project = session.get('Project', project_id)
        asset = version['asset']

        version_number = self._format_version(version['version'])

        parts = []
        parts.append(project['name'])

        if structure_names:
            parts.extend(structure_names)
        elif self.project_versions_prefix:
            # Add *project_versions_prefix* if configured and the version is
            # published directly under the project.
            parts.append(self.project_versions_prefix)

        parts.append(asset['name'])
        parts.append(asset["type"]["short"])
        parts.append(version_number)

        return [self.sanitise_for_filesystem(part) for part in parts]


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
        location.structure = StandardStructure()

        parents = []
        task = instance.context.data["ftrackTask"]
        for item in task['link'][:-1]:
            parents.append(session.get(item['type'], item['id']))
        project = parents[0]

        system = platform.system().lower()
        if system != "windows":
            system = "unix"

        location.accessor = ftrack_api.accessor.disk.DiskAccessor(
            prefix=os.path.join(project["disk"][system], project["root"])
        )

        for data in instance.data.get("ftrackComponentsList", []):
            data["component_location"] = location
