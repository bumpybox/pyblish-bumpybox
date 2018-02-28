from pyblish import api
from pyblish_bumpybox import inventory


class CollectRenderSetups(api.ContextPlugin):
    """Collect all render setups."""

    order = inventory.get_order(__file__, "CollectRenderSetups")
    hosts = ["maya"]
    label = "Render Setups"
    targets = ["process"]

    def process(self, context):
        import os
        import pymel
        import clique

        drg = pymel.core.PyNode("defaultRenderGlobals")

        for node in pymel.core.ls(type="renderLayer"):
            if node.name().startswith("defaultRenderLayer"):
                continue

            instance = context.create_instance(name=node.name())
            instance.data["families"] = ["rendersetup"]
            instance.data["family"] = "img"

            instance.add(node)

            publish_state = node.renderable.get()
            instance.data["publish"] = publish_state

            label = "{0} - rendersetup".format(node.name())
            instance.data["label"] = label

            # Generate collection
            first_image, last_image = pymel.core.renderSettings(
                firstImageName=True,
                lastImageName=True,
                fullPath=True,
                layer=node.name()
            )

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

            fmt = collection.format("{head}{padding}{tail}")
            for count in range(start_frame, end_frame + 1, step_frame):
                f = fmt % count
                collection.add(f)

            collection.padding = len(str(end_frame))

            instance.data["endFrame"] = end_frame
            instance.data["startFrame"] = start_frame
            instance.data["stepFrame"] = step_frame
            instance.data["collection"] = collection

            # Adding renderer to families
            instance.data["families"].append(drg.currentRenderer.get())

            # Assign toggle method
            def instance_toggled(instance, value):
                instance[0].renderable.set(value)
            instance.data["instanceToggled"] = instance_toggled
