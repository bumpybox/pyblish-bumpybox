from pyblish import api
from pyblish_bumpybox import inventory


class ExtractThumbnailImg(api.InstancePlugin):
    """Extracts thumbnail from review.

    Offset to get extraction data from studio plugins.
    """

    families = ["review"]
    order = inventory.get_order(__file__, "ExtractThumbnailImg")
    label = "Thumbnail"
    optional = True

    def process(self, instance):
        import os
        import subprocess

        input_file = instance.data["output_path"]
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

        data = {
            "assettype_data": {"short": instance.data["review_family"]},
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

        # From NukeStudio the reviews needs to be parented to the shots.
        if "trackItem.ftrackEntity.shot" in instance.data["families"]:
            data["asset_data"]["parent"] = instance.data["entity"]

        components.append(data)
        instance.data["ftrackComponentsList"] = components
