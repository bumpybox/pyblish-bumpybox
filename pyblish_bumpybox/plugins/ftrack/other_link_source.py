from pyblish import api
from pyblish_bumpybox import inventory


class OtherLinkSource(api.ContextPlugin):
    """Link the source version to all other versions."""

    order = inventory.get_order(__file__, "OtherLinkSource")
    label = "Ftrack Link Source"

    def process(self, context):

        # Collect source assetversion
        source_version = None
        for instance in context:
            # Filter to source instance
            families = [instance.data["family"]]
            families += instance.data.get("families", [])
            if "source" not in families:
                continue

            # Get AssetVersion from published component
            for data in instance.data.get("ftrackComponentsList", []):
                if "component" not in data.keys():
                    continue
                source_version = data["component"]["version"]

        # Skip if no source version were published
        if source_version is None:
            return

        for instance in context:
            # Filter to non source instance
            families = [instance.data["family"]] + instance.data["families"]
            if "source" in families:
                continue

            # Get AssetVersion from published component
            covered_versions = []
            for data in instance.data.get("ftrackComponentsList", []):
                if "component" not in data.keys():
                    continue

                # Prevent duplicate links being created with multiple
                # components on the same version.
                if data["component"]["version"]["id"] in covered_versions:
                    continue
                covered_versions.append(data["component"]["version"]["id"])

                existing_link = None
                for link in data["component"]["version"]["incoming_links"]:
                    if link["from_id"] == source_version["id"]:
                        existing_link = link

                if existing_link is None:
                    context.data["ftrackSession"].create(
                        "AssetVersionLink",
                        {
                            "from": source_version,
                            "to": data["component"]["version"]
                        }
                    )

        context.data["ftrackSession"].commit()
