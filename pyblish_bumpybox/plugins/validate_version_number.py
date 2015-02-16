import operator

import nuke
import nukescripts
import pyblish.api


@pyblish.api.log
class ValidateVersionNumber(pyblish.api.Validator):
    """Validates that the output naming and file name versioning is the same.
    """

    families = ['versionPaths']
    hosts = ['nuke']
    version = (0, 1, 0)
    optional = True

    def process_instance(self, instance):
        """
        """
        versions = {}
        for node in instance:
            path = node['file'].value()
            v = eval(nukescripts.version_get(path, 'v')[1])
            versions[path] = v

        path = instance.data('path')
        versions[path] = (eval(nukescripts.version_get(path, 'v')[1]))

        maxVersion = max(versions.iteritems(), key=operator.itemgetter(1))[1]

        success = True
        msg = 'Failed paths:\n'
        for version in versions:
            if versions[version] != maxVersion:
                success = False
                msg += version + '\n'

        msg += 'Max version number is: %s\n' % maxVersion

        if not success:
            raise Exception(msg)

    def repair_instance(self, instance):
        """Auto-repair corrects the output naming and file name
        to which ever is highest
        """
        pass
