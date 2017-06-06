import pyblish.api


class ExtractHieroFtrackComponents(pyblish.api.InstancePlugin):
    """ Extracting data to ftrack components.

    Offset to get shot data from "extract_ftrack_shot"
    """

    families = ["ftrack"]
    label = "Ftrack Components"
    hosts = ["hiero"]
    order = pyblish.api.ExtractorOrder + 0.1

    def process(self, instance):

        instance.data["ftrackComponentsList"] = instance.data.get(
            "ftrackComponentsList", []
        )
        session = instance.context.data["ftrackSession"]

        # Audio component
        if "audio" in instance.data:

            instance.data["ftrackComponentsList"].append({
                "assettype_data": {
                    "short": "audio",
                },
                "asset_data": {
                    "name": instance.data["name"],
                    "parent": session.get(
                        "Shot", instance.data["ftrackShotId"]
                    ),
                },
                "assetversion_data": {
                    "version": instance.context.data["version"],
                },
                "component_overwrite": True,
                "component_path": instance.data["audio"]
            })

        # Nuke scene component
        if ("nuke" in instance.data.get("families", []) and
           "collection" in instance.data):

            instance.data["ftrackComponentsList"].append({
                "assettype_data": {
                    "short": "scene",
                },
                "asset_data": {
                    "name": instance.data["name"],
                    "parent": session.get(
                        "Shot", instance.data["ftrackShotId"]
                    ),
                },
                "assetversion_data": {
                    "version": instance.context.data["version"],
                },
                "component_data": {
                    "name": "nuke",
                },
                "component_overwrite": True,
                "component_path": instance.data["collection"].format()
            })

        # Transcodes components
        if "transcodes" in instance.data:

            for collection in instance.data["transcodes"]:

                assettype = "img"
                if list(collection)[0].endswith(".mov"):
                    assettype = "mov"

                instance.data["ftrackComponentsList"].append({
                    "assettype_data": {
                        "short": assettype,
                    },
                    "asset_data": {
                        "name": instance.data["name"],
                        "parent": session.get(
                            "Shot", instance.data["ftrackShotId"]
                        ),
                    },
                    "assetversion_data": {
                        "version": instance.context.data["version"],
                    },
                    "component_data": {
                        "name": collection.tag_type,
                    },
                    "component_overwrite": True,
                    "component_path": collection.format()
                })
