import platform
import os

import nuke

import pyblish.api


class BumpyboxRoyalRenderExtractNuke(pyblish.api.InstancePlugin):
    """ Appending RoyalRender data to instances. """

    families = ["royalrender"]
    order = pyblish.api.ValidatorOrder
    label = "Royal Render"
    hosts = ["nuke"]

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

        data = {
            "Software": "Nuke",
            "Renderer": "",
            "SeqStart": first_frame,
            "SeqEnd": last_frame,
            "SeqStep": 1,
            "SeqFileOffset": 0,
            "Version": nuke.NUKE_VERSION_STRING,
            "SceneName": instance.context.data["currentFile"],
            "IsActive": False,
            "ImageDir": os.path.dirname(instance.data["collection"].format()),
            "ImageFilename": os.path.basename(
                instance.data["collection"].head
            ),
            "ImageExtension": instance.data["collection"].tail,
            "ImagePreNumberLetter": ".",
            "ImageSingleOutputFile": False,
            "SceneOS": scene_os,
            "Layer": instance.data["name"],
        }

        # Setting data
        instance.data["royalrenderData"] = data
