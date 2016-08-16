import os
import re
import traceback

import pyblish.api


class CollectSceneVersion(pyblish.api.ContextPlugin):
    """Finds version in the filename or passes the one found in the context
        Arguments:
        version (int, optional): version number of the publish
    """
    # offset to get the latest currentFile update
    order = pyblish.api.CollectorOrder + 0.1

    def process(self, context):

        filename = os.path.basename(context.data('currentFile'))

        try:
            prefix, version = self.version_get(filename, 'v')
            context.set_data('version', value=int(version))
            self.log.info('Scene Version: %s' % context.data('version'))
        except:
            msg = "Could not collect scene version:\n\n"
            msg += traceback.format_exc()
            self.log.warning(msg)

    def version_get(self, string, prefix):
        """Extract version information from filenames.  Code from Foundry's
        nukescripts.version_get()"""

        if string is None:
            raise ValueError("Empty version string - no match")

        regex = "[/_.]"+prefix+"\d+"
        matches = re.findall(regex, string, re.IGNORECASE)
        if not len(matches):
            msg = "No \"_"+prefix+"#\" found in \""+string+"\""
            raise ValueError(msg)
        return matches[-1:][0][1], re.search("\d+", matches[-1:][0]).group()


class CollectFtrackVersion(pyblish.api.ContextPlugin):
    """ Collects the version from the latest scene asset """

    # offset to get current version from CollectSceneVersion
    order = CollectSceneVersion.order + 0.1

    def process(self, context):
        try:
            import ftrack_api

            session = ftrack_api.Session()
            task_id = context.data['ftrackData']['Task']['id']
            query = 'select parent from Task where id is "%s"' % task_id
            task = session.query(query).one()
            query = 'select versions.version from Asset where parent.id is '
            query += '"%s" and type.short is "scene"' % task['parent']['id']
            query += ' and name is "%s"' % task['name']
            asset = session.query(query).one()

            # getting current version
            current_version = 1
            if 'version' in context.data:
                current_version = context.data['version']

            for version in asset['versions']:
                if current_version < version['version']:
                    current_version = version['version']

            context.data['version'] = current_version
        except:
            msg = "Could not collect ftrack version:\n\n"
            msg += traceback.format_exc()
            self.log.warning(msg)
