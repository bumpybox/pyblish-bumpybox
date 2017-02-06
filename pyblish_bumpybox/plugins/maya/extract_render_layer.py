import os
import sys
import subprocess

import pymel.core as pm
import maya.cmds as cmds

import pyblish.api


class BumpyboxMayaExtractRenderLayer(pyblish.api.InstancePlugin):
    """ Extracts the renderlayer to image output. """

    order = pyblish.api.ExtractorOrder
    families = ["renderlayer", "local"]
    optional = True
    label = "Render Layer"
    hosts = ["maya"]
    match = pyblish.api.Subset

    def process(self, instance):

        # Use RenderSequence if in 2017+
        if cmds.about(version=True) >= 2017:

            # Disble all render layer apart from the one that needs to render
            layers_state = []
            for layer in pm.ls(type="renderLayer"):
                layers_state.append((layer.renderable, layer.renderable.get()))
                if layer == instance[0]:
                    layer.renderable.set(True)
                else:
                    layer.renderable.set(False)

            # Setup render sequence settings. We are rendering all layers,
            # but since they are all disabled except the desired layer,
            # only that layer will be outputted.
            settings = {
                "renderSequenceRegion": 0,
                "renderSequenceAllLayers": 1,
                "renderSequenceAllCameras": 0,
                "renderSequenceAddToRenderView": 0,
                "renderSequenceAddAllLayers": 0,
                "renderSequenceAddAllCameras": 0
            }

            for key, value in settings.iteritems():
                cmds.optionVar(intValue=(key, value))

            # Execute cmds.RenderSequence()
            cmds.RenderSequence()

            # Restore layers state
            for attr, value in layers_state:
                attr.set(value)
        else:
            # Execute render in separate process.
            exe = os.path.dirname(sys.executable)
            render_executable = os.path.join(exe, "Render")
            layer_name = instance[0].name()
            scene_path = instance.context.data["currentFile"]
            project_directory = str(pm.system.Workspace.getPath().expand())

            args = [render_executable, "-rl", layer_name, scene_path, "-proj",
                    project_directory]

            self.log.debug("Executing: " + str(args))

            subprocess.call(args)

        # Check output files.
        for f in instance.data["collection"]:
            if not os.path.exists(f):
                instance.data["collection"].remove(f)
