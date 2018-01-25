import pyblish.api


class ExtractReview(pyblish.api.InstancePlugin):
    """Extract review hash value."""

    order = pyblish.api.ExtractorOrder
    label = "Review Hash"
    optional = True
    families = ["review"]
    hosts = ["nuke", "maya"]

    def md5(self, fname):
        import hashlib

        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def process(self, instance):
        import os

        hash_value = self.md5(instance.data["output_path"])
        md5_file = instance.data["output_path"].replace(
            os.path.splitext(instance.data["output_path"])[1],
            ".md5"
        )
        with open(md5_file, "w") as the_file:
            the_file.write(hash_value)


class ExtractReviewTranscode(pyblish.api.InstancePlugin):
    """Extracts review movie from image sequence or movie.

    Offset:
        pyblish_bumpybox.plugins.nuke.extract_review.ExtractReview
    """

    order = pyblish.api.ExtractorOrder + 0.02
    label = "Review Transcode"
    optional = True
    families = ["img", "mov"]
    targets = ["process.local"]

    def find_previous_index(self, index, indexes):
        """Finds the closest previous value in a list from a value."""

        data = []
        for i in indexes:
            if i >= index:
                continue
            data.append(index - i)

        return indexes[data.index(min(data))]

    def process(self, instance):

        if "collection" in instance.data.keys():
            self.process_image(instance)

        if "output_path" in instance.data.keys():
            self.process_movie(instance)

    def process_image(self, instance):
        import os
        import subprocess

        collection = instance.data["review_collection"]

        # Generate args.
        # Has to be yuv420p for compatibility with older players and smooth
        # playback. This does come with a sacrifice of more visible banding
        # issues.
        # -crf 18 is visually lossless.
        args = [
            "ffmpeg", "-y",
            "-start_number", str(min(collection.indexes)),
            "-framerate", str(instance.context.data["framerate"]),
            "-i", collection.format("{head}{padding}{tail}"),
            "-pix_fmt", "yuv420p",
            "-crf", "18",
            "-timecode", "00:00:00:01",
            "-vframes",
            str(max(collection.indexes) - min(collection.indexes) + 1),
            "-vf",
            "scale=trunc(iw/2)*2:trunc(ih/2)*2",
        ]

        if collection.format("{head}").endswith("."):
            args.append(collection.format("{head}mov"))
        else:
            args.append(collection.format("{head}.mov"))

        self.log.debug("Executing args: {0}".format(args))

        # Can't use subprocess.check_output, cause Houdini doesn't like that.
        p = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            cwd=os.path.dirname(args[-1])
        )

        output = p.communicate()[0]

        if p.returncode != 0:
            raise ValueError(output)

        self.log.debug(output)

    def process_movie(self, instance):
        import os
        import subprocess

        # Generate args.
        # Has to be yuv420p for compatibility with older players and smooth
        # playback. This does come with a sacrifice of more visible banding
        # issues.
        args = [
            "ffmpeg", "-y",
            "-i", instance.data["output_path"],
            "-pix_fmt", "yuv420p",
            "-crf", "18",
            "-timecode", "00:00:00:01",
        ]

        split = os.path.splitext(instance.data["output_path"])
        output_path = split[0] + "_review.mov"
        args.append(output_path)

        self.log.debug("Executing args: {0}".format(args))

        # Can't use subprocess.check_output, cause Houdini doesn't like that.
        p = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            cwd=os.path.dirname(args[-1])
        )

        output = p.communicate()[0]

        if p.returncode != 0:
            raise ValueError(output)

        self.log.debug(output)

        instance.data["output_path"] = output_path


class ExtractReviewTranscodeNukeStudio(ExtractReviewTranscode):
    """Extracts review movie from image sequence or movie.

    NukeStudio needs a processing workflow to merge with ExtractReviewTranscode

    Offset:
        pyblish_bumpybox.plugins.nukestudio.extract_review.ExtractReview
    """

    order = pyblish.api.ExtractorOrder + 0.02
    label = "Review Transcode"
    optional = True
    families = ["review"]
    targets = ["default"]
    hosts = ["nukestudio"]
