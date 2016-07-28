import os
import re
import shutil

import pyblish.api
import pipeline_schema


class IntegrateLocal(pyblish.api.InstancePlugin):

    label = "Local"
    families = ["img.local.*"]
    order = pyblish.api.IntegratorOrder

    def process(self, instance):

        if "outputPaths" not in instance.data:
            return

        data = pipeline_schema.get_data()
        ext = os.path.splitext(instance.data["family"])[1].replace("_", ".")
        data["extension"] = ext[1:]
        data["output_type"] = "img"
        data["name"] = str(instance)
        images_path = pipeline_schema.get_path("output_sequence", data=data)

        data["output_type"] = "mov"
        data["extension"] = "mov"
        movie_path = pipeline_schema.get_path("output_file", data=data)

        pattern = r"\.[0-9]{4}\."
        for path in instance.data["outputPaths"]:

            if ".%04d." in path:
                # ensuring parent path exists
                parent_path = os.path.dirname(images_path)
                if not os.path.exists(parent_path):
                    os.makedirs(parent_path)

                for f in instance.data["outputPaths"][path]:
                    basename = os.path.basename(f)
                    frame = int(re.findall(pattern, basename)[0][1:-1])
                    dst = images_path % frame

                    shutil.copy(f, dst)

                    # delete output
                    os.remove(f)

                    self.log.info("Moved {0} to {1}".format(f, dst))
            else:
                # ensuring parent path exists
                parent_path = os.path.dirname(movie_path)
                if not os.path.exists(parent_path):
                    os.makedirs(parent_path)

                shutil.copy(path, movie_path)

                # delete output
                os.remove(path)

                self.log.info("Moved {0} to {1}".format(path, movie_path))
