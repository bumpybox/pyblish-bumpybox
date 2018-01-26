from pyblish import api


class ExtractJSON(api.ContextPlugin):
    """ Extract all instances to a serialized json file. """

    order = api.IntegratorOrder + 1
    label = "JSON"
    hosts = ["maya", "houdini", "nuke"]
    targets = ["default", "process"]

    def process(self, context):
        import os
        import json
        import datetime
        import time

        import clique

        workspace = os.path.join(
            os.path.dirname(context.data["currentFile"]),
            "workspace",
            "instances"
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
                    self.log.debug(msg)

            output_data.append(data)

        timestamp = datetime.datetime.fromtimestamp(
            time.time()
        ).strftime("%S%M%H%d%m%Y")
        filename = timestamp + "_instances.json"

        with open(os.path.join(workspace, filename), "w") as outfile:
            outfile.write(json.dumps(output_data, indent=4, sort_keys=True))
