import pyblish.api


class CollectItems(pyblish.api.Collector):

    order = pyblish.api.Collector.order + 0.2

    def process(self, context):
        project = context.data('activeProject')

        selection = None
        try:
            selection = context.data('selection')
        except:
            pass

        valid_tags = ['ftrack', 'png', 'prores', 'dpx', 'copy', 'h264', 'nuke']

        video_tracks = []
        for seq in project.sequences():
            for vid in seq.videoTracks():
                if vid.isEnabled():
                    video_tracks.append(vid)

        for vid in video_tracks:
            for item in vid.items():

                check = False
                for tag in (item.tags() + vid.tags()):
                    if tag.name() in valid_tags:
                        check = True
                    data = tag.metadata()
                    if data.hasKey('type') and data.value('type') == 'task':
                        check = True

                if not check:
                    continue

                publish_state = True
                if selection:
                    if item not in selection:
                        publish_state = False

                instance = context.create_instance(name=item.name())
                families = []
                task_types = []
                for tag in (item.tags() + vid.tags()):
                    data = tag.metadata()
                    if data.hasKey('type') and data.value('type') == 'task':
                        families.append('task')
                        task_types.append(tag.name())
                    else:
                        families.append(tag.name())

                    instance.data['handles'] = 0
                    if data.hasKey('type') and data.value('type') == 'handles':
                        instance.data['handles'] = int(data.value('value'))

                instance.data['taskTypes'] = task_types
                instance.data['families'] = list(set(families))
                instance.add(item)
                instance.data['videoTrack'] = vid
                instance.data['publish'] = publish_state
                instance.data['family'] = 'trackItem'
