import pyblish.api


class CollectReviews(pyblish.api.ContextPlugin):
    """Generate reviews from "img" and "mov" instances.

    Offset:
        pyblish_bumpybox.plugins.collect_existing_files
    """

    # Offset to get created instances.
    order = pyblish.api.CollectorOrder + 0.3
    hosts = ["maya", "nuke", "nukeassist"]

    def process(self, context):
        import os

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

                    instance[0].getTransform().review.unlock()
                    instance[0].getTransform().review.set(value)
                    instance[0].getTransform().review.lock()
                except AttributeError:
                    pass

            instance.data["instanceToggled"] = instanceToggled

            families = item.data["families"] + [item.data["family"]]
            output_path = ""
            if "img" in families:
                output_path = item.data["collection"].format(
                    "{head}_review.mov"
                )
                if item.data["collection"].format("{head}").endswith("."):
                    output_path = item.data["collection"].format(
                        "{head}"
                    )[:-1]
                    output_path += "_review.mov"
                instance.data["review_family"] = "img"
            if "mov" in families:
                output_path = item.data["output_path"].replace(
                    os.path.splitext(item.data["output_path"])[1],
                    "_review.mov"
                )
                instance.data["review_family"] = "mov"

            instance.data["output_path"] = output_path

            # Previous versions should always be disabled.
            if item.data["family"] == "output":
                instance.data["publish"] = False
