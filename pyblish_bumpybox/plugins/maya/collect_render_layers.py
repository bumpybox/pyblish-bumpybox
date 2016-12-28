import os

import pymel

import pyblish.api
import clique


class BumpyboxMayaCollectRenderlayers(pyblish.api.ContextPlugin):
    """ Gathers all renderlayers. """

    order = pyblish.api.CollectorOrder
    hosts = ["maya"]
    label = "Render Layers"

    def process(self, context):

        # Getting render layers data.
        data = {}
        render_cams = []
        drg = pymel.core.PyNode("defaultRenderGlobals")
        for layer in pymel.core.ls(type="renderLayer"):

            # skipping defaultRenderLayers
            if layer.name().endswith("defaultRenderLayer"):
                continue

            layer_data = {}
            render_cams = []
            if layer.adjustments.get(multiIndices=True):
                for count in layer.adjustments.get(multiIndices=True):
                    if not layer.adjustments[count].plug.connections():
                        continue

                    if layer.adjustments[count].plug.connections()[0] == drg:
                        attr = layer.adjustments[count].plug
                        attr = attr.connections(plugs=True)[0]
                        layer_value = layer.adjustments[count].value.get()
                        layer_data[attr.name(includeNode=False)] = layer_value

                    plug = layer.adjustments[count].plug
                    for cam_attr in plug.connections(plugs=True,
                                                     type="camera"):
                        renderable = cam_attr.endswith("renderable")
                        layer_value = layer.adjustments[count].value.get()
                        if renderable and layer_value == 1.0:
                            name = cam_attr.split(".")[0]
                            render_cams.append(pymel.core.PyNode(name))

                render_pass = layer.connections(type="renderPass")
                layer_data["renderpasses"] = render_pass
            else:
                render_pass = layer.connections(type="renderPass")
                layer_data["renderpasses"] = render_pass

            layer_data["cameras"] = render_cams
            data[layer.name()] = layer_data

        # Create instances
        for layer in data:

            node = pymel.core.PyNode(layer)

            # Checking instance type. If object has attribute "remote" set to
            # true, its considered a "remote" instance.
            instance_type = "local"
            if hasattr(node, "remote"):
                attr = pymel.core.Attribute(node.name() + ".remote")
                if attr.get():
                    instance_type = "remote"
            else:
                pymel.core.addAttr(node,
                                   longName="remote",
                                   defaultValue=False,
                                   attributeType="bool")
                attr = pymel.core.Attribute(node.name() + ".remote")
                pymel.core.setAttr(attr, channelBox=True)

            instance = context.create_instance(name=layer)
            instance.data["families"] = ["renderlayer", instance_type, "img"]

            instance.data.update(data[layer])
            instance.add(node)

            publish_state = pymel.core.PyNode(layer).renderable.get()
            instance.data["publish"] = publish_state

            label = "{0} - renderlayer - {1}".format(layer, instance_type)
            instance.data["label"] = label

            # Generate collection
            first_image, last_image = pymel.core.renderSettings(
                firstImageName=True, lastImageName=True, fullPath=True,
                layer=layer
            )

            # Special case for vray that has it own extention setting
            renderer = drg.currentRenderer.get()
            if renderer == "vray":
                render_settings = pymel.core.PyNode("vraySettings")
                ext = "." + render_settings.imageFormatStr.get().split(" ")[0]

                first_image = os.path.splitext(first_image)[0] + ext

            collections = clique.assemble([first_image], minimum_items=1)[0]
            ext = os.path.splitext(first_image)[1]
            collection = collections[0]
            for col in collections:
                if col.tail == ext:
                    collection = col

            render_globals = pymel.core.PyNode("defaultRenderGlobals")
            start_frame = int(render_globals.startFrame.get())
            end_frame = int(render_globals.endFrame.get())
            step_frame = int(render_globals.byFrameStep.get())

            if "endFrame" in data[layer]:
                end_frame = int(data[layer]["endFrame"] * self.getFPS())
            if "startFrame" in data[layer]:
                start_frame = int(data[layer]["startFrame"] * self.getFPS())

            fmt = collection.format("{head}{padding}{tail}")
            for count in range(start_frame, end_frame + 1, step_frame):
                f = fmt % count
                collection.add(f)

            instance.data["collection"] = collection

    def getFPS(self):

        options = {"pal": 25, "game": 15, "film": 24, "ntsc": 30, "show": 48,
                   "palf": 50, "ntscf": 60}

        option = pymel.core.general.currentUnit(q=True, t=True)

        return options[option]
