from pyblish_bumpybox import plugin


class ExtractAudio(plugin.InstancePlugin):
    """ Extracting audio """

    families = ["audio"]
    label = "Audio"
    hosts = ["hiero"]
    order = plugin.ExtractorOrder
    optional = True

    def process(self, instance):
        import os

        item = instance[0]
        output_file = os.path.join(
            os.path.dirname(instance.context.data["currentFile"]),
            "workspace",
            item.parent().parent().name(),
            item.parent().name(),
            item.name() + ".wav"
        )

        output_dir = os.path.dirname(output_file)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        item.sequence().writeAudioToFile(output_file, item.timelineIn(),
                                         item.timelineOut())

        instance.data["audio"] = output_file
