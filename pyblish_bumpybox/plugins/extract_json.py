import os
import json

import pyblish.api
import clique


class BumpyboxExtractJSON(pyblish.api.ContextPlugin):
    """ Extract all instances to a serialized json file. """

    order = pyblish.api.IntegratorOrder + 1
    label = "JSON"
    hosts = ["maya", "houdini", "nuke"]

    def process(self, context):

        workspace = os.path.join(
            os.path.dirname(context.data["currentFile"]), "workspace"
        )

        if not os.path.exists(workspace):
            os.makedirs(workspace)

        output_data = []
        for instance in context:

            data = {}
            for key, value in instance.data.iteritems():
                if isinstance(value, clique.Collection):
                    value = value.format()

                try:
                    json.dumps(value)
                    data[key] = value
                except:
                    msg = "\"{0}\"".format(value)
                    msg += " in instance.data[\"{0}\"]".format(key)
                    msg += " could not be serialized."
                    self.log.warning(msg)

            output_data.append(data)

        with open(os.path.join(workspace, "instances.json"), "w") as outfile:
            outfile.write(json.dumps(output_data, indent=4, sort_keys=True))
