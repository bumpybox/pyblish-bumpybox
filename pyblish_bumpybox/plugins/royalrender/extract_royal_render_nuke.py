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
            instance.data["royalrenderJobs"] = jobs

            write_nodes.append(instance[0])

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
