import os
import re

import pyblish.api
import hiero


@pyblish.api.log
class ExtractPNG(pyblish.api.Extractor):
    """
    """

    order = pyblish.api.Extractor.order + 0.1
    families = ['transcode_png.trackItem']
    label = 'Transcode to PNG'

    def get_path(self, shot, track_name, context):

        ftrack_data = context.data('ftrackData')

        path = [ftrack_data['Project']['root']]
        path.append('renders')
        path.append('img_sequences')
        for p in reversed(shot.getParents()[:-1]):
            path.append(p.getName())

        path.append(shot.getName())
        path.append('transcode')

        # get version data
        version = 1
        if context.has_data('version'):
            version = context.data('version')
        version_string = 'v%s' % str(version).zfill(3)
        path.append(version_string)

        path.append('png_%s' % track_name)

        filename = [shot.getName(), version_string, 'png']
        path.append('.'.join(filename))

        return os.path.join(*path).replace('\\', '/')

    def frames_to_timecode(self, frames, framerate):

        h = str(int(frames / (3600 * framerate))).zfill(2)
        m = str(int(frames / (60 * framerate) % 60)).zfill(2)
        s = int(frames / framerate % 60)
        f = str((frames / framerate) - s).split('.')[1]

        return '%s:%s:%s.%s' % (h, m, str(s).zfill(2), f)

    def process(self, instance, context):

        item = instance[0]

        script_file = os.path.dirname(os.path.dirname(__file__))
        script_file = os.path.dirname(script_file)
        script_file = os.path.join(script_file, 'draft', 'mov_to_images.py')

        # collecting item info
        input_path = item.source().mediaSource().fileinfos()[0].filename()
        output_path = item.source().mediaSource().fileinfos()[0].filename()
        fps = item.sequence().framerate().toFloat()

        duration = item.sourceOut() - item.sourceIn() + 1
        duration = self.frames_to_timecode(duration, fps)
        source_in = self.frames_to_timecode(item.sourceIn(), fps)

        # skipping if not launched from ftrack
        if context.has_data('ftrackData'):
            import ftrack

            ftrack_data = context.data('ftrackData')
            parent = ftrack.Project(ftrack_data['Project']['id'])
            parent_path = [parent.getName()]

            if 'Episode' in ftrack_data:
                parent = ftrack.Sequence(ftrack_data['Episode']['id'])
                parent_path.append(parent.getName())

            naming = '([a-z]+[0-9]{3})'
            names = re.findall(naming, item.name())
            if len(names) > 1:
                [sequence_name, shot_name] = names
            else:
                shot_name = names[0]
                if 'Sequence' in ftrack_data:
                    sequence_name = ftrack_data['Sequence']['name']
                else:
                    sequence_name = item.sequence().name()

            parent_path.append(sequence_name)
            parent_path.append(item.name())

            shot = ftrack.getShot(parent_path)

            output_path = self.get_path(shot,
                                    instance.data('videoTrack').name(), context)

            if not os.path.exists(os.path.dirname(output_path)):
                os.makedirs(os.path.dirname(output_path))

        # collecting output data
        basename = os.path.splitext(os.path.basename(output_path))[0]
        filename = '.'.join([basename, '####', 'png'])
        output_path = os.path.join(os.path.dirname(output_path), filename)

        if context.has_data('ftrackData'):
            asset = shot.createAsset('transcode', 'img')
            version = None
            for v in asset.getVersions():
                if v.getVersion() == context.data('version'):
                    version = v

            if not version:
                version = asset.createVersion()
                version.set('version', value=context.data('version'))

            version.publish()

            path = output_path.replace('####', '%04d')
            try:
                name = 'png_%s' % instance.data('videoTrack').name()
                version.createComponent(name=name, path=path)
            except:
                msg = 'Components "png" already exists. '
                msg += 'Please delete them manually first.'
                self.log.warning(msg)

        # adding deadline data
        job_data = {'Group': 'python27','Pool': 'medium',
                    'Plugin': 'CommandLine',
                    'OutputFilename0': output_path, 'Frames': 0}

        plugin_data = {}

        args = '-i <QUOTE>%s<QUOTE>' % input_path
        args += ' -ss %s' % source_in
        args += ' -t %s' % duration
        args += ' <QUOTE>%s<QUOTE>' % output_path.replace('####', '%04d')
        plugin_data['Arguments'] = args

        path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        path = os.path.dirname(os.path.dirname(os.path.dirname(path)))
        path = os.path.join(path, 'ffmpeg', 'bin', 'ffmpeg.exe')
        plugin_data['Executable'] = path

        data = {'job': job_data, 'plugin': plugin_data}
        instance.set_data('deadlineData', value=data)
