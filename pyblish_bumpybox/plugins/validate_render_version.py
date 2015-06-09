import re

import pyblish.api


@pyblish.api.log
class ValidateRenderVersion(pyblish.api.Validator):
    """Validates the version number of the render compared to the file name
    """

    families = ['deadline.render']
    hosts = ['*']
    version = (0, 1, 0)

    def version_get(self, string, prefix, suffix = None):
        """Extract version information from filenames.  Code from Foundry's nukescripts.version_get()"""

        if string is None:
           raise ValueError, "Empty version string - no match"

        regex = "[/_.]"+prefix+"\d+"
        matches = re.findall(regex, string, re.IGNORECASE)
        if not len(matches):
            msg = "No version string found in \""+string+"\""
            msg += "\n\nAdd 'v[version_number].'"
            raise ValueError, msg
        return (matches[-1:][0][1], re.search("\d+", matches[-1:][0]).group())

    def process(self, instance):
        path = instance.context.data('currentFile')
        version_number = int(self.version_get(path, 'v')[1])

        path = instance.data('deadlineOutput')
        v = int(self.version_get(path, 'v')[1])

        if version_number != v:
            msg = 'Version number %s is not the same as ' % v
            msg += 'file version number %s.' % version_number
            msg += "Please change %s's output to the same version" % instance
            msg += " number as the scene file."
            raise Exception(msg)
