import os

import pyblish.api
import hiero


class CollectItems(pyblish.api.Collector):
    """ Collects all enabled video tracks and track items tagged
    """

    order = pyblish.api.Collector.order + 0.2

    def process(self, context):
        project = context.data('activeProject')

        selection = None
        try:
            selection = context.data('selection')
        except:
            pass

        valid_tags = ['ftrack', 'png', 'prores', 'dpx', 'copy', 'h264']
        ftrack_tags = ['png', 'prores', 'dpx', 'copy']

        video_tracks = []
        for seq in project.sequences():
            for vid in seq.videoTracks():
                if vid.isEnabled():
                    video_tracks.append(vid)

        for vid in video_tracks:
            for item in vid.items():

                publish_state = True
                if selection:
                    if item not in selection:
                        publish_state = False

                tags = item.tags() + vid.tags()
                for tag in tags:

                    if tag.name() not in valid_tags:
                        continue

                    name = vid.parent().name() + ':'
                    name += vid.name() + ': ' + item.name()
                    name += " (%s)" % tag.name()

                    if name not in context:
                        instance = context.create_instance(name=name)
                        fam = '%s.trackItem' % tag.name()
                        instance.set_data('family', value=fam)
                        instance.add(item)
                        instance.set_data('videoTrack', value=vid)
                        instance.set_data('publish', value=publish_state)

                        # adding ftrack data to activate processing
                        if tag.name() in ftrack_tags:
                            instance.set_data('ftrackComponents', value={})

                            ext = item.source().mediaSource().fileinfos()[0]
                            ext = os.path.splitext(ext.filename())[1]

                            asset_type = 'img'
                            if ext == '.mov':
                                asset_type = 'mov'

                            instance.set_data('ftrackAssetType',
                                                            value=asset_type)

                            ftrack_data = context.data('ftrackData')
                            asset_name = ftrack_data['Task']['name']
                            instance.set_data('ftrackAssetName',
                                                            value=asset_name)

        context[:] = sorted(context,
                                key=lambda instance: instance.data("family"))
