import pyblish.api

import hiero


class CollectHieroItems(pyblish.api.ContextPlugin):
    """ Collect Hiero instances.

    Collects all trackitem tagged with the preset tags. If a tag has "family"
    in its meta data, this family will also be added to the instance.
    """

    order = pyblish.api.CollectorOrder
    label = "Collect"
    hosts = ["hiero"]

    def process(self, context):
        project = context.data("activeProject")

        selection = None
        try:
            selection = hiero.selection
        except:
            pass

        video_tracks = []
        for seq in project.sequences():
            for vid in seq.videoTracks():
                if vid.isEnabled():
                    video_tracks.append(vid)

        for vid in video_tracks:
            for item in vid.items():
                tags = list(set(item.tags() + vid.tags()))

                if not tags:
                    continue

                instance = context.create_instance(name=item.name())
                instance.add(item)

                # Assigning families from tags.
                families = ["trackItem"]
                for tag in tags:
                    data = tag.metadata().dict()
                    if "tag.family" in data:
                        families.append(data["tag.family"])

                    families.append(tag.name())

                instance.data["families"] = list(set(families))

                # Publishable state from whether the track/item is enabled, and
                # whether its in the selection if there is a selection.
                instance.data["publish"] = item.isEnabled()
                if selection:
                    track_items = False
                    for track_item in hiero.selection:
                        if isinstance(item, hiero.core.TrackItem):
                            track_items = True

                    if track_items and item not in selection:
                        instance.data["publish"] = False
