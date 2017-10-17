import platform
import os

import nuke

import pyblish.api


class ExtractRoyalRenderNuke(pyblish.api.InstancePlugin):
    """ Appending RoyalRender data to instances. """

    order = pyblish.api.ExtractorOrder
    label = "Royal Render Nuke"
    hosts = ["nuke"]
    targets = ["process.royalrender"]

    def process(self, instance):

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
            "SceneName": instance.context.data["currentFile"],
            "ImageDir": os.path.dirname(instance.data["collection"].format()),
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
