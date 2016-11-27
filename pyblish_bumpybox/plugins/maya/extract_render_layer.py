import os
import sys
import subprocess

import pymel

import pyblish.api


class BumpyboxMayaExtractRenderLayer(pyblish.api.InstancePlugin):
    """ Extracts the renderlayer to image output. """

    order = pyblish.api.ExtractorOrder
    families = ["renderlayer"]
    optional = True
    label = "Render Layer"
    hosts = ["maya"]

    def process(self, instance):

        # Execute render in separate process.
        exe = os.path.dirname(sys.executable)
        render_executable = os.path.join(exe, "Render")
        layer_name = instance[0].name()
        scene_path = instance.context.data["currentFile"]
        project_directory = str(pymel.core.system.Workspace.getPath().expand())

        args = [render_executable, "-rl", layer_name, scene_path, "-proj",
                project_directory]

        self.log.debug("Executing: " + str(args))

        subprocess.call(args)

        # Check output files.
        for f in instance.data["collection"]:
            if not os.path.exists(f):
                instance.data["collection"].remove(f)
