import os
import pyblish.api


class ValidateReview(pyblish.api.InstancePlugin):
    """Validate all review files exists."""

    order = pyblish.api.ValidatorOrder
    label = "Review"
    optional = True
    families = ["review"]

    def process(self, instance):

        # Validate collection
        missing_files = []
        for f in instance.data.get("collection", []):
            if not os.path.exists(f):
                missing_files.append(f)

        msg = "Review files missing: {0}".format(missing_files)
        assert not missing_files, msg

        # Validate output
        if "output_path" in instance.data.keys():
            msg = "Review file missing: {0}".format(
                instance.data["output_path"]
            )
            assert os.path.exists(instance.data["output_path"]), msg
