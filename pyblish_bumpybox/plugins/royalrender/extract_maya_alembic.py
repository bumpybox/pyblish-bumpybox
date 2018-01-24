from pyblish import api


class ExtractMovie(api.InstancePlugin):
    """Appending RoyalRender movie job data."""

    families = ["alembic"]
    order = api.ExtractorOrder
    label = "Royal Render Alembic"
    targets = ["process.royalrender"]
    hosts = ["maya"]

    def process(self, instance):
        import sys
        import os

        import alembic_export

        import pymel

        mayapy_executable = os.path.join(
            os.path.dirname(sys.executable),
            os.path.basename(sys.executable).replace("maya", "mayapy")
        )
        script = alembic_export.__file__
        alembic_file = instance.data["output_path"]
        frame_start = int(pymel.core.playbackOptions(q=True, min=True))
        frame_end = int(pymel.core.playbackOptions(q=True, max=True))

        # Validate whether we can strip namespaces.
        strip_namespaces = True
        root_names = []
        for member in instance[0]:
            if member.name().split(":")[-1] not in root_names:
                root_names.append(member.name().split(":")[-1])
            else:
                strip_namespaces = False

        if not strip_namespaces:
            msg = "Can't strip namespaces, because of conflicting root names."
            msg += " Nodes will be renamed."
            self.log.warning(msg)

        # Ensure output directory exists.
        if not os.path.exists(os.path.dirname(alembic_file)):
            os.makedirs(os.path.dirname(alembic_file))

        # Generate batch script
        data = (
            "\"{0}\" \"{1}\" -mayaFile \"{2}\" -alembicFile \"{3}\" "
            "-frameRange {4} \"{5}\" -uvWrite -worldSpace "
            "-wholeFrameGeo -eulerFilter -writeVisibility".format(
                mayapy_executable,
                script,
                instance.context.data["currentFile"],
                alembic_file,
                frame_start,
                frame_end
            )
        )

        for name in root_names:
            data += " -root %s " % name

        if strip_namespaces:
            data += " -stripNamespaces 0"

        file_path = alembic_file.replace(".abc", ".bat")
        with open(file_path, "w") as f:
            f.write(data)

        # Generate job data
        data = {
            "Software": "Execute",
            "SeqStart": 1,
            "SeqEnd": 1,
            "SeqStep": 1,
            "SeqFileOffset": 0,
            "Version": 1.0,
            "SceneName": file_path,
            "ImageDir": os.path.dirname(alembic_file),
            "ImageFilename": os.path.basename(alembic_file),
            "ImageExtension": "",
            "ImagePreNumberLetter": ".",
            "ImageSingleOutputFile": "true",
            "SceneOS": "win",
            "Layer": "",
            "IsActive": True,
        }

        # Adding job
        jobs = instance.data.get("royalrenderJobs", [])
        jobs.append(data)
        instance.data["royalrenderJobs"] = jobs
