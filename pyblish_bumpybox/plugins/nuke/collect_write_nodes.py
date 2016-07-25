import os

import nuke
import pyblish.api


class CollectWriteNodes(pyblish.api.Collector):
    """Selects all write nodes"""

    label = "Collect Write Nodes"
    order = pyblish.api.Collector.order + 0.4

    def process(self, context):

        # storing plugin data
        plugin_data = {"EnforceRenderOrder": True}

        plugin_data["NukeX"] = nuke.env["nukex"]

        plugin_data["Version"] = nuke.NUKE_VERSION_STRING.split("v")[0]

        # creating instances per write node
        for node in nuke.allNodes():
            if node.Class() == "Write":
                instance = context.create_instance(name=node.name())
                instance.data["family"] = "deadline.render"
                instance.data["families"] = ["deadline"]
                instance.add(node)

                output = node["file"].getValue()

                instance.set_data("publish", not node["disable"].getValue())

                # setting job data
                job_data = {}
                if instance.has_data("deadlineData"):
                    job_data = instance.data("deadlineData")["job"].copy()

                output_file = output

                if "%" in output_file:
                    padding = int(output_file.split("%")[1][0:2])
                    padding_string = "%0{0}d".format(padding)
                    tmp = "#" * padding
                    output_file = output_file.replace(padding_string, tmp)

                job_data["OutputFilename0"] = output_file
                job_data["Plugin"] = "Nuke"

                name = os.path.basename(context.data["currentFile"])
                name = os.path.splitext(name)[0] + " - " + str(instance)
                job_data["Name"] = name

                # frame range
                start_frame = int(nuke.root()["first_frame"].getValue())
                end_frame = int(nuke.root()["last_frame"].getValue())
                if node["use_limit"].getValue():
                    start_frame = int(node["first"].getValue())
                    end_frame = int(node["last"].getValue())

                instance.data["firstFrame"] = start_frame
                instance.data["endFrame"] = end_frame
                job_data["Frames"] = "%s-%s\n" % (start_frame, end_frame)

                # setting plugin data
                plugin_data = plugin_data.copy()
                plugin_data["WriteNode"] = node.name()
                plugin_data["SceneFile"] = context.data["currentFile"]

                current_file = instance.context.data["currentFile"]
                data = {"job": job_data, "plugin": plugin_data,
                        "order": int(node["render_order"].value()),
                        "auxiliaryFiles": [current_file]}
                instance.set_data("deadlineData", value=data)

                # adding ftrack data to activate processing
                instance.set_data("ftrackComponents", value={})
                instance.set_data("ftrackAssetType", value="img")
