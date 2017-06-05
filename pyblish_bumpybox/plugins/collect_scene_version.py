import os
import re
import traceback

import pyblish.api


class CollectSceneVersion(pyblish.api.ContextPlugin):
    """ Collects scene version from filename or passes the one found in
    the context.
    """
    # offset to get the latest currentFile update
    order = pyblish.api.CollectorOrder + 0.1
    label = "Scene Version"

    def process(self, context):

        filename = os.path.basename(context.data("currentFile"))

        try:
            prefix, version = self.version_get(filename, "v")
            context.set_data("version", value=int(version))
            self.log.info("Scene Version: %s" % context.data("version"))
        except:
            msg = "Could not collect scene version:\n\n"
            msg += traceback.format_exc()
            self.log.warning(msg)

    def version_get(self, string, prefix):
        """ Extract version information from filenames.  Code from Foundry"s
        nukescripts.version_get()
        """

        if string is None:
            raise ValueError("Empty version string - no match")

        regex = "[/_.]"+prefix+"\d+"
        matches = re.findall(regex, string, re.IGNORECASE)
        if not len(matches):
            msg = "No \"_"+prefix+"#\" found in \""+string+"\""
            raise ValueError(msg)
        return matches[-1:][0][1], re.search("\d+", matches[-1:][0]).group()
