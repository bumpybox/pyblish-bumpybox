import pyblish.api


class ValidateReview(pyblish.api.InstancePlugin):
    """Validate all review files exists."""

    order = pyblish.api.ValidatorOrder
    label = "Review"
    optional = True
    families = ["review"]

    def md5(self, fname):
        import hashlib

        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def process(self, instance):
        import os

        msg = "Review movie file is missing: {0}".format(
            instance.data["output_path"]
        )
        assert os.path.exists(instance.data["output_path"]), msg

        # Compare hash values of current to previous review file, which should
        # be different.
        md5_file = instance.data["output_path"].replace(
            os.path.splitext(instance.data["output_path"])[1],
            ".md5"
        )

        if not os.path.exists(md5_file):
            return

        previous_hash_value = ""
        with open(md5_file, "r") as the_file:
            previous_hash_value = the_file.read()

        current_hash_value = self.md5(instance.data["output_path"])

        msg = "{0} is the same as previous published review.".format(
            instance.data["output_path"]
        )
        assert current_hash_value != previous_hash_value, msg
