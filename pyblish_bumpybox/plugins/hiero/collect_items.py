import pyblish.api
import hiero


class CollectItems(pyblish.api.Collector):
    """ Collects all enabled video tracks and track items tagged
    """

    def process(self, context):
        project = context.data('activeProject')

        video_tracks = []
        for seq in project.sequences():

            instance = context.create_instance(name=seq.name())
            instance.set_data('family', value='sequence')
            instance.add(seq)

            for vid in seq.videoTracks():
                if vid.isEnabled():
                    video_tracks.append(vid)

        for vid in video_tracks:
            for item in vid.items():
                tags = item.tags() + vid.tags()
                for tag in tags:
                    name = vid.name() + ': ' + item.name()
                    name += " (%s)" % tag.name()

                    if name not in context:
                        instance = context.create_instance(name=name)
                        fam = '%s.trackItem' % tag.name()
                        instance.set_data('family', value=fam)
                        instance.add(item)
                        instance.set_data('videoTrack', value=vid)

        context[:] = sorted(context, key=lambda instance: instance.data("family"))
