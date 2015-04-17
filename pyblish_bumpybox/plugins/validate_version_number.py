import operator
import traceback

import nuke
import nukescripts
import pyblish.api


@pyblish.api.log
class ValidateVersionNumber(pyblish.api.Validator):
    """Validates the version number of write nodes compared to the file name
    """

    families = ['writeNode', 'prerenders']
    hosts = ['nuke']
    version = (0, 1, 0)

    def process_instance(self, instance):
        path = nuke.root().name()
        version_number = int(nukescripts.version_get(path, 'v')[1])

        path = instance[0]['file'].value()
        v = int(nukescripts.version_get(path, 'v')[1])

        if version_number != v:
            msg = 'Version number %s is not the same as ' % v
            msg += 'file version number %s' % version_number
            raise Exception(msg)

    def repair_instance(self, instance):
        """Sets the version number of the output to the same as the file name
        """
        path = nuke.root().name()
        version_number = int(nukescripts.version_get(path, 'v')[1])

        path = instance[0]['file'].value()
        v = int(nukescripts.version_get(path, 'v')[1])

        new_path = nukescripts.version_set(path, 'v', v, version_number)
        instance[0]['file'].setValue(new_path)
