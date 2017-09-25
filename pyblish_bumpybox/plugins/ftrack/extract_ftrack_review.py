import json

import pyblish.api


class ExtractFtrackReview(pyblish.api.InstancePlugin):
    """Extracts movie from image sequence for review.

    Offset to get extraction data from studio plugins.
    """

    families = ["img"]
    order = pyblish.api.ExtractorOrder + 0.1
    label = "Review"
    optional = True

    def process(self, instance):

        collection = instance.data.get("collection", [])
        output_file = collection.format("{head}.mov")

        # Add Ftrack review component
        components = instance.data.get("ftrackComponentsList", [])
        server_location = instance.context.data["ftrackSession"].query(
            "Location where name is \"ftrack.server\""
        ).one()
        components.append(
            {
              "assettype_data": {
                "short": "img",
              },
              "asset_data": instance.data.get("asset_data"),
              "assetversion_data": {
                "version": instance.data.get(
                    "version", instance.context.data["version"]
                ),
              },
              "component_data": {
                "name": "ftrackreview-mp4",
                "metadata": {
                    "ftr_meta": json.dumps({
                        "frameIn": list(collection.indexes)[0],
                        "frameOut": list(collection.indexes)[-1],
                        "frameRate": instance.context.data["framerate"]
                    })
                }
              },
              "component_overwrite": True,
              "component_location": server_location,
              "component_path": output_file
            }
        )
        instance.data["ftrackComponentsList"] = components
