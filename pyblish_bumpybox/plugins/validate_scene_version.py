import re

import pyblish.api


@pyblish.api.log
class ValidateSceneVersion(pyblish.api.Validator):
    """Validates the existence of version number on the scene
    """

    families = ['scene']
    hosts = ['*']
    version = (0, 1, 0)
    label = 'Scene Version'

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

        self.version_get(instance.data('workPath'), 'v')
        self.version_get(instance.data('publishPath'), 'v')
