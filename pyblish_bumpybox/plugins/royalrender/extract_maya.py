from pyblish import api


class ExtractMaya(api.ContextPlugin):
    """ Appending RoyalRender data to instances. """

    families = ["img"]
    order = api.ExtractorOrder
    label = "Royal Render"
    hosts = ["maya"]
    targets = ["process.royalrender"]

    def process(self, instance):
        import platform
        import os

        import pymel.core as pm
        import pymel.versions

        version = pymel.versions.current()
        version = str(version/100) + "." + str(version % 100).zfill(2)

        defaultRenderGlobals = pymel.core.PyNode("defaultRenderGlobals")

        scene_os = ""
        if platform.system() == "Windows":
            scene_os = "win"

        camera = None
        for camera in pymel.core.ls(type="camera"):
            if camera.renderable.get():
                break

        file_prefix = defaultRenderGlobals.imageFilePrefix.get()

        data = instance.data.get("royalrenderData", {})

        data.update({
            "Software": "Maya",
            "Renderer": instance.data["renderer"],
            "SeqStart": instance.data["startFrame"],
            "SeqEnd": instance.data["endFrame"],
            "SeqStep": instance.data["stepFrame"],
            "SeqFileOffset": 0,
            "Version": version,
            "SceneName": instance.context.data["currentFile"],
            "IsActive": False,
            "ImageDir": os.path.join(
                pm.Workspace.getPath(), pm.Workspace.fileRules["images"]
            ),
            "ImageFilename": file_prefix.replace("<RenderLayer>", "<Layer>"),
            "ImageExtension": instance.data["collection"].tail,
            "ImagePreNumberLetter": ".",
            "ImageSingleOutputFile": False,
            "SceneOS": scene_os,
            "Camera": camera.getTransform(),
            "Layer": instance.data["name"],
            "SceneDatabaseDir": pm.Workspace.getPath(),
            "ImageFramePadding": instance.data["collection"].padding,
        })

        # SubmitterParameter
        submit_params = data.get("SubmitterParameter", [])
        submit_params.append("OverwriteExistingFiles=1~1")
        data["SubmitterParameter"] = submit_params

        # Vray
        renderer = defaultRenderGlobals.currentRenderer.get()
        if renderer == "vray":
            settings = pymel.core.PyNode("vraySettings")
            data["ImageFilename"] = settings.fileNamePrefix.get()

        # Setting data
        instance.data["royalrenderData"] = data
