import os
import re

import pymel
import pyblish.api


class ExtractAlembic(pyblish.api.Extractor):
    """
    """

    families = ['alembic', 'alembic.asset', 'alembic.camera']
    optional = True
    label = 'Alembic'

    def get_ftrack_path(self, instance):

        path = []
        filename = []

        # get ftrack data
        ftrack_data = instance.context.data('ftrackData')
        path.append(ftrack_data['Project']['root'])
        child_path = []
        parent = False
        parent_name = ftrack_data['Project']['name']
        path.append('renders')
        path.append('cache')

        try:
            name = ftrack_data['Asset_Build']['name'].replace(' ', '_').lower()
            asset_type = ftrack_data['Asset_Build']['type'].lower()
            path.append(asset_type)
            path.append(name)
            parent_name = name
        except:
            self.log.info('No asset build found.')

        try:
            name = ftrack_data['Episode']['name'].replace(' ', '_').lower()
            child_path.append(name)
            parent_name = name
        except:
            self.log.info('No episode found.')

        try:
            name = ftrack_data['Sequence']['name'].replace(' ', '_').lower()
            child_path.append(name)
            parent_name = name
        except:
            self.log.info('No sequences found.')

        try:
            name = ftrack_data['Shot']['name'].replace(' ', '_').lower()
            child_path.append(name)
            parent_name = name
        except:
            self.log.info('No shot found.')

        path.extend(child_path)

        task_name = ftrack_data['Task']['name'].replace(' ', '_').lower()
        path.append(task_name)

        version = 1
        if instance.context.has_data('version'):
            version = instance.context.data('version')
        version_string = 'v%s' % str(version).zfill(3)

        path.append(version_string)

        filename.append(parent_name)
        filename.append(task_name)
        filename.append(version_string)
        filename.append(re.sub('[^\w\-_\. ]', '_', str(instance)))
        filename.append('abc')
        path.append('.'.join(filename))

        return os.path.join(*path).replace('\\', '/')

    def get_path(self, instance, context):
        current_file = context.data('currentFile')
        current_dir = os.path.dirname(current_file)

        path = [current_dir, 'cache']

        # get version data
        version = 1
        if instance.context.has_data('version'):
            version = instance.context.data('version')
        version_string = 'v%s' % str(version).zfill(3)

        filename = [re.sub('[^\w\-_\. ]', '_', str(instance))]

        filename.append(version_string)
        filename.append('abc')

        path.append('.'.join(filename))

        return os.path.join(*path).replace('\\', '/')

    def process(self, instance, context):

        path = self.get_path(instance, context)

        # ftrack dependencies
        if context.has_data('ftrackData'):
            path = self.get_ftrack_path(instance)

            components = {str(instance): {'path': path}}

            instance.set_data('ftrackComponents', value=components)

        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        nodesString = ''
        stripNamespaces = True
        root_names = []
        for member in instance:
            nodesString += '-root %s ' % member.name()
            if member.name().split(':')[-1] not in root_names:
                root_names.append(member.name().split(':')[-1])
            else:
                stripNamespaces = False

        frame_start = int(pymel.core.playbackOptions(q=True, min=True))
        frame_end = int(pymel.core.playbackOptions(q=True, max=True))

        cmd = '-frameRange %s %s' % (frame_start, frame_end)
        if stripNamespaces:
            cmd += ' -stripNamespaces'
        else:
            msg = "Can't strip namespaces, because of conflicting root names."
            msg += " Nodes will be renamed."
            self.log.warning(msg)
        cmd += ' -uvWrite -worldSpace -wholeFrameGeo '
        cmd += '-eulerFilter '
        cmd += '-writeVisibility %s -file "%s"' % (nodesString, path)

        pymel.core.general.refresh(suspend=True)
        try:
            pymel.core.AbcExport(j=cmd)
        except Exception as e:
            raise e
        pymel.core.general.refresh(suspend=False)
