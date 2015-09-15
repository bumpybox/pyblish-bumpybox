import os
import re

import pymel
import pyblish.api
import ftrack


class ExtractAlembic(pyblish.api.Extractor):
    """
    """

    families = ['alembic', 'alembic.asset', 'alembic.camera']

    def get_path(self, instance):

        path = []
        filename = []

        # get ftrack data
        ftrack_data = instance.context.data('ftrackData')
        project = ftrack.Project(id=ftrack_data['Project']['id'])
        path.append(ftrack_data['Project']['root'])
        path.append('renders')
        path.append('cache')

        try:
            seq_name = ftrack_data['Sequence']['name'].replace(' ', '_').lower()
            path.append(seq_name)
        except:
            self.log.info('No sequences found.')

        try:
            shot_name = ftrack_data['Shot']['name'].replace(' ', '_').lower()
            path.append(shot_name)
            filename.append(shot_name)
        except:
            self.log.info('No shot found.')

        task_name = ftrack_data['Task']['name'].replace(' ', '_').lower()
        path.append(task_name)
        filename.append(task_name)

        # get version data
        version = 1
        if instance.context.has_data('version'):
            version = instance.context.data('version')
        version_string = 'v%s' % str(version).zfill(3)
        path.append(version_string)

        filename.append(version_string)

        filename.append(re.sub('[^\w\-_\. ]', '_', str(instance)))
        filename.append('abc')

        path.append('.'.join(filename))

        return os.path.join(*path).replace('\\', '/')

    def process(self, instance, context):

        root = instance[0]
        path = self.get_path(instance)

        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        nodesString = '-root ' + root.name()

        frame_start = int(pymel.core.playbackOptions(q=True, min=True))
        frame_end = int(pymel.core.playbackOptions(q=True, max=True))

        cmd = '-frameRange %s %s' % (frame_start, frame_end)
        cmd += ' -stripNamespaces -uvWrite -worldSpace -wholeFrameGeo '
        cmd += '-writeVisibility %s -file "%s"' % (nodesString, path)

        pymel.core.AbcExport(j=cmd)

        # ftrack data
        ftrack_data = context.data('ftrackData')

        components = {str(instance): {'path': path}}

        instance.set_data('ftrackComponents', value=components)
