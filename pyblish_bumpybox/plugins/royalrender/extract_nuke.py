from pyblish import api
from pyblish_bumpybox import inventory


class ExtractNuke(api.ContextPlugin):
    """ Appending RoyalRender data to instances. """

    order = inventory.get_order(__file__, "ExtractNuke")
    label = "Royal Render Nuke"
    hosts = ["nuke", "nukeassist"]
    families = ["royalrender"]
    targets = ["process.royalrender"]

    def duplicate_node(self, node, to_file=None):
        """Slightly convoluted but reliable(?) way duplicate a node, using
        the same functionality as the regular copy and paste.
        Could almost be done tidily by doing:
        for knobname in src_node.knobs():
            value = src_node[knobname].toScript()
            new_node[knobname].fromScript(value)
        ..but this lacks some subtly like handling custom knobs
        to_file can be set to a string, and the node will be written to a
        file instead of duplicated in the tree
        """
        import nuke

        # Store selection
        orig_selection = nuke.selectedNodes()

        # Select only the target node
        [n.setSelected(False) for n in nuke.selectedNodes()]
        node.setSelected(True)

        # If writing to a file, do that, restore the selection and return
        if to_file is not None:
            nuke.nodeCopy(to_file)
            [n.setSelected(False) for n in orig_selection]
            return

        # Copy the selected node and clear selection again
        nuke.nodeCopy("%clipboard%")
        node.setSelected(False)

        if to_file is None:
            # If not writing to a file, call paste function, and the new node
            # becomes the selected
            nuke.nodePaste("%clipboard%")
            new_node = nuke.selectedNode()

        # Restore original selection
        [n.setSelected(False) for n in nuke.selectedNodes()]
        [n.setSelected(True) for n in orig_selection]

        return new_node

    def process(self, context):
        import platform
        import os
        import time
        import shutil
        import subprocess

        import nuke

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

            # Generate baked colorspace job
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

            # Reformat for pixelaspect ratio
            node = previous_node = nuke.createNode("Reformat")

            node["type"].setValue(2)
            nuke.selectedNode()["scale"].setValue(
                [1, 1.0 / instance[0].pixelAspect()]
            )
            node["resize"].setValue(5)

            temporary_nodes.append(node)

            # Viewer process node
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

            viewer_nodes = nuke.allNodes(filter="Viewer")
            if viewer_nodes:
                viewer_node = nuke.allNodes(filter="Viewer")[0]
                if viewer_node["input_process"].value():
                    input_process_node = self.duplicate_node(
                        nuke.toNode(viewer_node["input_process_node"].value())
                    )
                    input_process_node.setInput(0, previous_node)
                    previous_node = input_process_node
                    temporary_nodes.append(input_process_node)

            write_node = nuke.createNode("Write")
            write_node["name"].setValue(
                instance[0]["name"].value() + "_review"
            )
            review_files = instance.data["collection"].format(
                "{head}_review.%04d.jpeg"
            )
            if instance.data["collection"].format("{head}").endswith("."):
                review_files = instance.data["collection"].format(
                    "{head}"
                )[:-1]
                review_files += "_review.%04d.jpeg"
            write_node["file"].setValue(review_files.replace("\\", "/"))
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
                "ImageDir": os.path.dirname(review_files),
                "ImageFilename": os.path.basename(review_files).replace(
                    ".%04d.jpeg", ""
                ),
                "ImageExtension": ".jpeg",
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

            # Generate batch script
            output_file = review_files.replace("%04d.jpeg", "mov")
            args = [
                "ffmpeg", "-y",
                "-start_number", str(first_frame),
                "-framerate", str(instance.context.data["framerate"]),
                "-i", review_files.replace("%", "%%"),
                "-pix_fmt", "yuv420p",
                "-crf", "18",
                "-timecode", "00:00:00:01",
                "-vframes", str(last_frame - first_frame + 1),
                "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
                output_file
            ]

            batch_file = review_files.replace("%04d.jpeg", "bat")

            if not os.path.exists(os.path.dirname(batch_file)):
                os.makedirs(os.path.dirname(batch_file))

            with open(batch_file, "w") as the_file:
                the_file.write(subprocess.list2cmdline(args))

            # Generate movie job
            data = {
                "Software": "Execute",
                "SeqStart": 1,
                "SeqEnd": 1,
                "SeqStep": 1,
                "SeqFileOffset": 0,
                "Version": 1.0,
                "SceneName": batch_file,
                "ImageDir": os.path.dirname(output_file),
                "ImageFilename": os.path.basename(output_file),
                "ImageExtension": "",
                "ImagePreNumberLetter": ".",
                "ImageSingleOutputFile": "true",
                "SceneOS": "win",
                "Layer": "",
                "PreID": 2,
                "IsActive": True,
                "WaitForPreID": 1
            }

            submit_params = data.get("SubmitterParameter", [])
            submit_params.append("OverwriteExistingFiles=1~1")
            submit_params.append("AllowLocalSceneCopy=0~0")
            submit_params.append("Priority=1~75")
            data["SubmitterParameter"] = submit_params

            jobs.append(data)

            # Adding jobs
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
