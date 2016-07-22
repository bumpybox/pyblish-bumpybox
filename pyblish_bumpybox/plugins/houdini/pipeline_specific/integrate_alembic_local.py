import os
import shutil

import pyblish.api
import pipeline_schema


class IntegrateAlembicLocal(pyblish.api.InstancePlugin):
    """ Integrates alembic output """

    families = ["cache.local.alembic"]
    label = "Alembic Local"
    order = pyblish.api.IntegratorOrder
    optional = True

    def process(self, instance):

        # get output path
        data = pipeline_schema.get_data()
        data["extension"] = "abc"
        data["output_type"] = "cache"
        data["name"] = str(instance)
        output_file = pipeline_schema.get_path("output_file", data=data)

        # copy output
        if not os.path.exists(os.path.dirname(output_file)):
            os.makedirs(os.path.dirname(output_file))

        shutil.copy(instance.data["outputPath"], output_file)

        # delete output
        os.remove(instance.data["outputPath"])

        self.log.info("Moved {0} to {1}".format(instance.data["outputPath"],
                                                output_file))

        # ftrack data
        name = str(instance)
        instance.data["ftrackComponents"][name] = {"path": output_file}
