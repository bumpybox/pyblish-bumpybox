from pyblish import api
from pyblish_bumpybox import inventory
reload(inventory)


class ExtractNukeStudio(api.InstancePlugin):
    """Extract source footage to Ftrack components."""

    order = inventory.get_order(__file__, "ExtractNukeStudio")
    label = "Ftrack NukeStudio"
    hosts = ["nukestudio"]
    families = ["trackItem.ftrackEntity.shot"]

    def process(self, instance):

        collated_items = []
        for video_track in instance.data["item"].parent().parent().items():
            for track_item in video_track.items():
                if instance.data["item"].name() == track_item.name():
                    collated_items.append(track_item)

        # Filter to exr images
        file_path = None
        item = None
        for track_item in collated_items:
            path = track_item.source().mediaSource().fileinfos()[0].filename()
            if path.endswith(".exr"):
                file_path = path
                item = track_item

        component_path = "{0} [{1}-{2}]".format(
            file_path,
            int(item.mapTimelineToSource(item.timelineIn())),
            int(item.mapTimelineToSource(item.timelineOut()))
        )

        location = instance.context.data["ftrackSession"].query(
            "Location where name is \"ftrack.unmanaged\""
        ).one()

        components = instance.data.get("ftrackComponentsList", [])
        components.append(
            {
                "assettype_data": {"short": "img"},
                "asset_data": {"parent": instance.data["entity"]},
                "assetversion_data": {
                    "version": instance.context.data["version"]
                },
                "component_path": component_path,
                "component_location": location
            }
        )
        instance.data["ftrackComponentsList"] = components
