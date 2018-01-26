from pyblish import api
from pyblish_bumpybox import inventory


class ExtractOutputDirectory(api.ContextPlugin):
    """Extracts the output path for any collection or single output_path."""

    order = inventory.get_order(__file__, "ExtractOutputDirectory")
    label = "Output Directory"
    optional = True
    targets = ["process"]

    def process(self, instance):
        import os

        path = None

        if "collection" in instance.data.keys():
            path = instance.data["collection"].format()

        if "output_path" in instance.data.keys():
            path = instance.data["output_path"]

        if not path:
            return

        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
