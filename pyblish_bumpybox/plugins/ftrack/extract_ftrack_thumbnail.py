import os
import subprocess

import pyblish.api


class ExtractFtrackThumbnailImg(pyblish.api.InstancePlugin):
    """Extracts thumbnail from image sequence.

    Offset to get extraction data from studio plugins.
    """

    families = ["img"]
    order = pyblish.api.ExtractorOrder + 0.1
    label = "Thumbnail - Images"
    optional = True

    def process(self, instance):

        collection = instance.data.get("collection", [])

        output_file = collection.format("{head}_thumbnail.jpeg")
        input_file = list(collection)[0]
        args = [
            "ffmpeg", "-y",
            "-gamma", "2.2", "-i", input_file,
            "-vf", "scale=300:-1", output_file
        ]

        self.log.debug("Executing args: {0}".format(args))

        # Can"t use subprocess.check_output, cause Houdini doesn"t like that.
        p = subprocess.Popen(args, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, stdin=subprocess.PIPE)

        output = p.communicate()[0]

        if p.returncode != 0:
            raise ValueError(output)

        self.log.debug(output)

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
                "name": "thumbnail",
              },
              "component_overwrite": True,
              "component_location": server_location,
              "component_path": output_file,
              "thumbnail": True
            }
        )
        instance.data["ftrackComponentsList"] = components


class ExtractFtrackThumbnailMov(pyblish.api.InstancePlugin):
    """Extracts thumbnail from image sequence.

    Offset to get extraction data from studio plugins.
    """

    families = ["mov"]
    order = pyblish.api.ExtractorOrder + 0.1
    label = "Thumbnail - Movie"
    optional = True

    def process(self, instance):

        input_file = instance.data.get("baked_colorspace_movie", "output_path")
        ext = os.path.splitext(input_file)[1]
        output_file = input_file.replace(ext, "_thumbnail.jpeg")
        args = [
            "ffmpeg", "-y",
            "-i", input_file,
            "-vf", "scale=300:-1",
            "-vframes", "1",
            output_file
        ]

        self.log.debug("Executing args: {0}".format(args))

        # Can"t use subprocess.check_output, cause Houdini doesn"t like that.
        p = subprocess.Popen(args, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, stdin=subprocess.PIPE)

        output = p.communicate()[0]

        if p.returncode != 0:
            raise ValueError(output)

        self.log.debug(output)

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
                "name": "thumbnail",
              },
              "component_overwrite": True,
              "component_location": server_location,
              "component_path": output_file,
              "thumbnail": True
            }
        )
        instance.data["ftrackComponentsList"] = components
