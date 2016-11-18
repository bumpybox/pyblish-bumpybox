import traceback

import pyblish.api


class BumpyboxFtrackCollectVersion(pyblish.api.ContextPlugin):
    """ Collects the version from the latest scene asset """

    # offset to get current version from CollectSceneVersion
    order = pyblish.api.CollectorOrder + 0.2
    label = "Version"

    def process(self, context):
        try:
            import ftrack_api

            session = ftrack_api.Session()
            task_id = context.data["ftrackData"]["Task"]["id"]
            query = "select parent from Task where id is \"%s\"" % task_id
            task = session.query(query).one()
            query = "select versions.version from Asset where parent.id is "
            query += "\"%s\" and type.short is " % task["parent"]["id"]
            query += "\"scene\" and name is \"%s\"" % task["name"]
            asset = session.query(query).one()

            # getting current version
            current_version = 1
            if "version" in context.data:
                current_version = context.data["version"]

            for version in asset["versions"]:
                if current_version < version["version"]:
                    current_version = version["version"]

            context.data["version"] = current_version
        except:
            msg = "Could not collect ftrack version:\n\n"
            msg += traceback.format_exc()
            self.log.warning(msg)
