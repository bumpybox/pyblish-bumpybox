import re
import os

import pyblish.api
import hiero
import ftrack


@pyblish.api.log
class ExtractAudio(pyblish.api.Extractor):
    """ Creates ftrack shots by the name of the shot
    """

    families = ['ftrack.trackItem']
    order = pyblish.api.Extractor.order + 0.1
    label = 'Audio'
    optional = True

    def get_path(self, shot, context):

        ftrack_data = context.data('ftrackData')

        path = [ftrack_data['Project']['root']]
        path.append('renders')
        path.append('audio')
        for p in reversed(shot.getParents()[:-1]):
            path.append(p.getName())

        path.append(shot.getName())

        # get version data
        version = 1
        if context.has_data('version'):
            version = context.data('version')
        version_string = 'v%s' % str(version).zfill(3)

        filename = [shot.getName(), version_string, 'wav']
        path.append('.'.join(filename))

        return os.path.join(*path).replace('\\', '/')

    def process(self, instance, context):

        # skipping if not launched from ftrack
        if not context.has_data('ftrackData'):
            return

        ftrack_data = context.data('ftrackData')
        parent = ftrack.Project(ftrack_data['Project']['id'])
        parent_path = [parent.getName()]

        if 'Episode' in ftrack_data:
            parent = ftrack.Sequence(ftrack_data['Episode']['id'])
            parent_path.append(parent.getName())

        naming = '([a-z]+[0-9]{3})'
        for item in instance:
            [sequence_name, shot_name] = re.findall(naming, item.name())

            path = list(parent_path)
            path.append(sequence_name)
            path.append(item.name())
            shot = ftrack.getShot(path)

            path = self.get_path(shot, context)

            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))

            if os.path.exists(path):
                msg = 'Audio file already exists. Please delete manually first.'
                self.log.warning(msg)
            else:
                item.sequence().writeAudioToFile(path, item.sourceIn(),
                                                            item.sourceOut())

            asset = shot.createAsset(item.name(), 'audio')
            version = None
            for v in asset.getVersions():
                if v.getVersion() == context.data('version'):
                    version = v

            if not version:
                version = asset.createVersion()
                version.set('version', value=context.data('version'))

            version.publish()

            try:
                version.createComponent(name='main', path=path)
                version.createComponent(name='wav', path=path)
            except:
                msg = 'Components "main" and "wav" already exists. '
                msg += 'Please delete them manually first.'
                self.log.warning(msg)
