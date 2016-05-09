import os
import tempfile

import pyblish.api
import hiero
from pyblish_bumpybox.plugins.hiero import utils


class ExtractNuke(pyblish.api.Extractor):

    families = ['nuke']
    label = 'Nuke Script'
    order = pyblish.api.Extractor.order + 0.1

    def process(self, instance, context):

        item = instance[0]
        file_path = item.source().mediaSource().fileinfos()[0].filename()
        fps = item.sequence().framerate().toFloat()
        handles = instance.data['handles']

        reverse = False
        if item.playbackSpeed() < 0:
            reverse = True

        retime = False
        if item.playbackSpeed() != 1.0:
            retime = True

        first_frame = int(item.sourceIn() + 1) - handles
        first_frame_offset = 1
        last_frame = int(item.sourceOut() + 1) + handles
        last_frame_offset = last_frame - first_frame + 1
        if reverse:
            first_frame = int(item.sourceOut() + 1)
            first_frame_offset = 1
            last_frame = int(item.sourceIn() + 1)
            last_frame_offset = last_frame - first_frame + 1

        # creating exr transcode nuke script
        nukeWriter = hiero.core.nuke.ScriptWriter()

        root_node = hiero.core.nuke.RootNode(first_frame_offset,
                                             last_frame_offset)
        nukeWriter.addNode(root_node)

        width = item.parent().parent().format().width()
        height = item.parent().parent().format().height()

        item.addToNukeScript(script=nukeWriter, firstFrame=first_frame_offset,
                             includeRetimes=True, retimeMethod='Frame',
                             startHandle=handles, endHandle=handles)

        write_path = utils.get_path(instance, 'exr', self.log, sequence=True)
        write_node = hiero.core.nuke.WriteNode(write_path)
        write_node.setKnob('file_type', 'exr')
        write_node.setKnob('metadata', 'all metadata')
        nukeWriter.addNode(write_node)

        script_path = os.path.join(tempfile.gettempdir(),
                                   str(instance) + '.nk')
        nukeWriter.writeToDisk(script_path)

        # adding deadline data
        job_data = {'Group': 'nuke_9', 'Pool': 'medium', 'Plugin': 'Nuke',
                    'OutputFilename0': write_path, 'ChunkSize': 10,
                    'Frames': '{0}-{1}'.format(first_frame_offset,
                                               last_frame_offset),
                    'LimitGroups': 'nuke'}

        plugin_data = {'NukeX': False, 'Version': '9.0',
                       'EnforceRenderOrder': True, 'SceneFile': ''}

        data = {'job': job_data, 'plugin': plugin_data,
                'auxiliaryFiles': [script_path]}
        instance.set_data('deadlineData', value=data)

        # creating shot nuke script
        nukeWriter = hiero.core.nuke.ScriptWriter()

        # root node
        root_node = hiero.core.nuke.RootNode(first_frame_offset,
                                             last_frame_offset, fps=fps)
        if retime:
            last_frame = abs(int(round(last_frame_offset /
                                       item.playbackSpeed())))
            root_node = hiero.core.nuke.RootNode(first_frame_offset,
                                                 last_frame, fps=fps)
        fmt = item.parent().parent().format()
        root_node.setKnob('format', '{0} {1}'.format(fmt.width(),
                                                     fmt.height()))
        nukeWriter.addNode(root_node)

        # primary read node
        read_node = hiero.core.nuke.ReadNode(write_path,
                                             width=width,
                                             height=height,
                                             firstFrame=first_frame_offset,
                                             lastFrame=last_frame_offset)
        nukeWriter.addNode(read_node)
        last_node = read_node

        if reverse or retime:

            last_frame = last_frame_offset
            if retime:
                last_frame = abs(int(round(last_frame_offset /
                                           item.playbackSpeed())))
            retime_node = hiero.core.nuke.RetimeNode(first_frame_offset,
                                                     last_frame_offset,
                                                     first_frame_offset,
                                                     last_frame,
                                                     reverse=reverse)
            retime_node.setKnob('shutter', 0)
            retime_node.setInputNode(0, read_node)
            nukeWriter.addNode(retime_node)
            last_node = retime_node

        write_path = os.path.join(tempfile.gettempdir(),
                                  str(instance) + '.exr')
        write_node = hiero.core.nuke.WriteNode(write_path, inputNode=last_node)
        write_node.setKnob('file_type', 'exr')
        write_node.setKnob('metadata', 'all metadata')
        nukeWriter.addNode(write_node)

        # secondary read nodes
        seq = item.parent().parent()
        time_in = item.timelineIn()
        time_out = item.timelineOut()

        items = []
        for count in range(time_in, time_out):
            items.extend(seq.trackItemsAt(count))

        items = list(set(items))
        items.remove(item)

        last_frame = abs(int(round(last_frame_offset /
                                   item.playbackSpeed())))

        for i in items:
            src = i.source().mediaSource().fileinfos()[0].filename()
            in_frame = i.mapTimelineToSource(time_in) + 1 - handles
            out_frame = i.mapTimelineToSource(time_out) + 1 + handles
            read_node = hiero.core.nuke.ReadNode(src, width=width,
                                                 height=height,
                                                 firstFrame=in_frame,
                                                 lastFrame=out_frame)
            nukeWriter.addNode(read_node)

            retime_node = hiero.core.nuke.RetimeNode(in_frame, out_frame,
                                                     first_frame_offset,
                                                     last_frame)
            retime_node.setKnob('shutter', 0)
            retime_node.setInputNode(0, read_node)
            nukeWriter.addNode(retime_node)

        # get file path
        path = []
        filename = []

        ftrack_data = instance.context.data('ftrackData')
        path.append(ftrack_data['Project']['root'])

        parent_dir = 'shots'
        parent_names = []
        for p in instance.data['ftrackShot'].getParents():
            try:
                parent_dir = p.get('objecttypename').lower() + 's'
                parent_names.append(p.get('name'))
            except:
                pass
        path.append(parent_dir)

        for p in reversed(parent_names):
            path.append(p)

        name = str(instance).split('--')[-1]
        path.append(name)
        path.append('publish')

        filename.append(name)

        # get version data
        version = 1
        if instance.context.has_data('version'):
            version = instance.context.data('version')
        version_string = 'v%s' % str(version).zfill(3)

        filename.append(version_string)
        filename.append('nk')

        path.append('.'.join(filename))

        file_path = os.path.join(*path).replace('\\', '/')

        # create directories
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))

        # create nuke script
        nukeWriter.writeToDisk(file_path)

        # publishing to ftrack
        asset = instance.data['ftrackShot'].createAsset(name, 'scene')

        # removing existing version
        for v in asset.getVersions():
            if v.getVersion() == context.data['version']:
                v.delete()

        # creating new version
        version = asset.createVersion()
        version.set('version', context.data['version'])
        version.createComponent(name='nuke', path=file_path)
        version.publish()
