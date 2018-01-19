import platform
import os
import time
import shutil

import nuke

import pyblish.api


class ExtractRoyalRenderNuke(pyblish.api.ContextPlugin):
    """ Appending RoyalRender data to instances. """

    order = pyblish.api.ExtractorOrder
    label = "Royal Render Nuke"
    hosts = ["nuke", "nukeassist"]
    families = ["royalrender"]
    targets = ["process.royalrender"]

    def process(self, context):

        write_nodes = []
        temporary_nodes = []
        for instance in context:

            families = [instance.data] + instance.data["families"]
            if "royalrender" not in families:
                continue

            if not instance.data["publish"]:
                continue

            # Get scene path
            scene_path = os.path.join(
                os.path.dirname(instance.context.data["currentFile"]),
                "workspace",
                "render",
                "{0}_{1}".format(
                    time.strftime("%Y%m%d%H%M%S"),
                    os.path.basename(instance.context.data["currentFile"])
                )
            )
            if instance.context.data.get("royalrenderSceneName", ""):
                scene_path = instance.context.data["royalrenderSceneName"]
            else:
                instance.context.data["royalrenderSceneName"] = scene_path

            # Get OS
            scene_os = ""
            if platform.system() == "Windows":
                scene_os = "win"

            # Get frame range
            node = instance[0]
            first_frame = nuke.root()["first_frame"].value()
            last_frame = nuke.root()["last_frame"].value()

            if node["use_limit"].value():
                first_frame = node["first"].value()
                last_frame = node["last"].value()

            # Generate data
            data = {
                "Software": "Nuke",
                "Renderer": "",
                "SeqStart": first_frame,
                "SeqEnd": last_frame,
                "SeqStep": 1,
                "SeqFileOffset": 0,
                "Version": nuke.NUKE_VERSION_STRING,
                "SceneName": scene_path,
                "ImageDir": os.path.dirname(
                    instance.data["collection"].format()
                ),
                "ImageFilename": os.path.basename(
                    instance.data["collection"].head
                ),
                "ImageExtension": instance.data["collection"].tail,
                "ImagePreNumberLetter": ".",
                "ImageSingleOutputFile": False,
                "SceneOS": scene_os,
                "Layer": instance.data["name"],
                "PreID": 0,
                "IsActive": True,
            }

            # SubmitterParameter
            submit_params = data.get("SubmitterParameter", [])
            submit_params.append("OverwriteExistingFiles=1~1")
            submit_params.append("AllowLocalSceneCopy=0~0")
            data["SubmitterParameter"] = submit_params

            # Adding job
            jobs = instance.data.get("royalrenderJobs", [])
            jobs.append(data)
            write_nodes.append(instance[0])

            # Generate review job
            node = previous_node = nuke.createNode("Read")
            node["file"].setValue(
                instance.data["collection"].format(
                    "{head}{padding}{tail}"
                )
            )
            node["first"].setValue(int(first_frame))
            node["origfirst"].setValue(int(first_frame))
            node["last"].setValue(int(last_frame))
            node["origlast"].setValue(int(last_frame))

            index = instance[0]["colorspace"].getValue()
            node["colorspace"].setValue(
                node["colorspace"].enumName(int(index))
            )
            temporary_nodes.append(node)

            viewer_process_node = nuke.ViewerProcess.node()
            dag_node = None
            if viewer_process_node:
                dag_node = nuke.createNode(viewer_process_node.Class())
                dag_node.setInput(0, previous_node)
                previous_node = dag_node
                temporary_nodes.append(dag_node)
                # Copy viewer process values
                excludedKnobs = ["name", "xpos", "ypos"]
                for item in viewer_process_node.knobs().keys():
                    if item not in excludedKnobs and item in dag_node.knobs():
                        x1 = viewer_process_node[item]
                        x2 = dag_node[item]
                        x2.fromScript(x1.toScript(False))
            else:
                self.log.warning("No viewer node found.")

            write_node = nuke.createNode("Write")
            write_node["name"].setValue(
                instance[0]["name"].value() + "_review"
            )
            path = instance.data["collection"].format(
                "{head}_review.%04d.jpeg"
            )
            write_node["file"].setValue(path.replace("\\", "/"))
            write_node["file_type"].setValue("jpeg")
            write_node["raw"].setValue(1)
            write_node["_jpeg_quality"].setValue(1)
            write_node.setInput(0, previous_node)
            temporary_nodes.append(write_node)

            data = {
                "Software": "Nuke",
                "Renderer": "",
                "SeqStart": first_frame,
                "SeqEnd": last_frame,
                "SeqStep": 1,
                "SeqFileOffset": 0,
                "Version": nuke.NUKE_VERSION_STRING,
                "SceneName": scene_path,
                "ImageDir": os.path.dirname(path),
                "ImageFilename": os.path.basename(
                    instance.data["collection"].format(
                        "{head}_review"
                    )
                ),
                "ImageExtension": os.path.splitext(path)[1],
                "ImagePreNumberLetter": ".",
                "ImageSingleOutputFile": False,
                "SceneOS": scene_os,
                "Layer": write_node.name(),
                "PreID": 1,
                "IsActive": True,
                "WaitForPreID": 0
            }

            submit_params = data.get("SubmitterParameter", [])
            submit_params.append("OverwriteExistingFiles=1~1")
            submit_params.append("AllowLocalSceneCopy=0~0")
            data["SubmitterParameter"] = submit_params

            jobs.append(data)
            instance.data["royalrenderJobs"] = jobs

        # Convert write paths to absolute
        paths = []
        for node in write_nodes:
            paths.append(node["file"].value())
            node["file"].setValue(nuke.filename(node))

        nuke.scriptSave()

        # Create render copy
        scene_path = context.data["royalrenderSceneName"]
        if not os.path.exists(os.path.dirname(scene_path)):
            os.makedirs(os.path.dirname(scene_path))

        shutil.copy(instance.context.data["currentFile"], scene_path)

        # Revert write paths back
        for node in write_nodes:
            node["file"].setValue(paths[write_nodes.index(node)])

        # Clean up
        for node in temporary_nodes:
            nuke.delete(node)

        nuke.scriptSave()
