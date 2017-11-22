import pyblish.api


class CollectFtrackReviews(pyblish.api.ContextPlugin):
    """Generate Ftrack reviews from "img" and "mov" instances."""

    # Offset to get created instances.
    order = pyblish.api.CollectorOrder + 0.3

    def process(self, context):

        items = []
        for item in context:
            families = item.data["families"] + [item.data["family"]]
            if "img" in families or "mov" in families:
                items.append(item)

        for item in items:
            instance = context.create_instance(name=item.data["name"])
            instance.data["label"] = item.data["label"]
            instance.data["family"] = "review"
            instance.add(item[0])

            publish = item.data["publish"]
            try:
                if "review" in item[0].knobs():
                    publish = item[0]["review"].value()
            except AttributeError:
                pass

            try:
                import pymel.core
                if hasattr(item[0].getTransform(), "review"):
                    attr = pymel.core.Attribute(
                        item[0].getTransform().name() + ".review"
                    )
                    publish = attr.get()
            except ImportError:
                pass

            instance.data["publish"] = publish

            def instanceToggled(instance, value):
                try:
                    import nuke
                    # Removing and adding the knob to support NukeAssist, where
                    # you can't modify the knob value directly.
                    if "review" in instance[0].knobs():
                        instance[0].removeKnob(instance[0]["review"])
                    knob = nuke.Boolean_Knob(
                        "review", "Review"
                    )
                    knob.setValue(value)
                    instance[0].addKnob(knob)
                except ImportError:
                    pass

                try:
                    if not hasattr(instance[0].getTransform(), "review"):
                        pymel.core.addAttr(
                            instance[0].getTransform(),
                            longName="review",
                            defaultValue=False,
                            attributeType="bool"
                        )
                        attr = pymel.core.Attribute(
                            instance[0].getTransform().name() + ".review"
                        )
                        pymel.core.setAttr(attr, channelBox=True)

                    instance[0].getTransform().review.set(value)
                except AttributeError:
                    pass

            instance.data["instanceToggled"] = instanceToggled

            families = item.data["families"] + [item.data["family"]]
            if "img" in families:
                instance.data["collection"] = item.data["collection"]
            if "mov" in families:
                instance.data["output_path"] = item.data["output_path"]
