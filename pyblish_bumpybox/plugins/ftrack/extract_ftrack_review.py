import os
import json
import subprocess

import pyblish.api


class ExtractFtrackImgReview(pyblish.api.InstancePlugin):
    """Extracts movie from image sequence for review.

    Offset to get extraction data from studio plugins.
    """

    families = ["img"]
    order = pyblish.api.ExtractorOrder + 0.2
    label = "Review"
    optional = True

    def process(self, instance):

        collection = instance.data.get("collection", [])
        output_file = collection.format("{head}.mov")

        if not os.path.exists(output_file):
            raise IOError("\"{0}\" not found.".format(output_file))

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
                        "frameRate": str(instance.context.data["framerate"])
                    })
                }
              },
              "component_overwrite": True,
              "component_location": server_location,
              "component_path": output_file
            }
        )
        instance.data["ftrackComponentsList"] = components


class ExtractFtrackMovReview(pyblish.api.InstancePlugin):
    """Extracts review movie component.

    Offset to get extraction data from studio plugins.
    """

    families = ["mov"]
    order = pyblish.api.ExtractorOrder + 0.2
    label = "Review"
    optional = True

    def process(self, instance):

        path = os.path.splitext(instance.data["output_path"])[0]
        path += "_review.mov"

        if not os.path.exists(path):
            raise IOError("\"{0}\" not found.".format(path))

        cmd = (
            "ffprobe -v error -count_frames -select_streams v:0 -show_entries "
            "stream=nb_read_frames -of default=nokey=1:noprint_wrappers=1 "
            "\"{0}\""
        )
        frame_count = subprocess.check_output(cmd.format(path))

        cmd = (
            "ffprobe -v 0 -of compact=p=0:nk=1 -select_streams 0 -show_entries"
            " stream=r_frame_rate \"{0}\""
        )
        # ffprobe returns a math string, hence the "eval"
        frame_rate = eval(subprocess.check_output(cmd.format(path)))

        # Add Ftrack review component
        components = instance.data.get("ftrackComponentsList", [])
        server_location = instance.context.data["ftrackSession"].query(
            "Location where name is \"ftrack.server\""
        ).one()
        components.append(
            {
              "assettype_data": {
                "short": "mov",
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
                        "frameIn": 1,
                        "frameOut": frame_count,
                        "frameRate": str(frame_rate)
                    })
                }
              },
              "component_overwrite": True,
              "component_location": server_location,
              "component_path": path
            }
        )
        instance.data["ftrackComponentsList"] = components
