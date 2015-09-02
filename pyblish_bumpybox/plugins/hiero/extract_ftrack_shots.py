import re
import os

import pyblish.api
import hiero
import ftrack


class ExtractFtrackShots(pyblish.api.Extractor):
    """ Creates ftrack shots by the name of the shot
    """

    families = ['ftrack.trackItem']
    label = 'Ftrack Shots'
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
            parent_name = ftrack_data['Episode']['name']
            parent_path.append(parent_name)

            parent = ftrack.getSequence(parent_path)

        item = instance[0]

        # creating sequence
        sequence = None
        if 'Sequence' in ftrack_data:
            sequence = ftrack.Sequence(ftrack_data['Sequence']['id'])
            parent_path.append(ftrack_data['Sequence']['name'])
        else:
            naming = r'([a-z]{1,2}[0-9]{3}\b)'
            result = re.findall(naming, item.name())
            sequence_name = item.name().replace(result[0], '')
            if not sequence_name:
                sequence_name = item.sequence().name()

            try:
                sequence = parent.createSequence(sequence_name)

                msg = 'Creating new sequence with name'
                msg += ' "%s"' % sequence_name
                self.log.info(msg)
            except:
                path = list(parent_path)
                path.append(sequence_name)
                sequence = ftrack.getSequence(path)

        parent_path.append(sequence.getName())

        # creating shot
        try:
            shot = sequence.createShot(item.name())

            shot.set('fstart', value=item.sourceIn())
            shot.set('fend', value=item.sourceOut())

            path = self.get_path(shot, context)

            instance.set_data('ftrackId', value=shot.getId())

            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))

            item.sequence().writeAudioToFile(path, item.sourceIn(),
                                                    item.sourceOut())

            msg = 'Creating new shot with name'
            msg += ' "%s"' % item.name()
            self.log.info(msg)
        except:
            path = list(parent_path)
            path.append(item.name())
            shot = ftrack.getShot(path)

            instance.set_data('ftrackId', value=shot.getId())

            update = False
            if shot.get('fstart') != item.sourceIn():
                shot.set('fstart', value=item.sourceIn())

                update = True

                msg = 'Updating frame start for shot with name'
                msg += ' "%s"' % item.name()
                self.log.info(msg)

            if shot.get('fend') != item.sourceOut():
                shot.set('fend', value=item.sourceOut())

                update = True

                msg = 'Updating frame end for shot with name'
                msg += ' "%s"' % item.name()
                self.log.info(msg)

            if update:
                path = self.get_path(shot, context)

                if not os.path.exists(os.path.dirname(path)):
                    os.makedirs(os.path.dirname(path))

                item.sequence().writeAudioToFile(path, item.sourceIn(),
                                                        item.sourceOut())
