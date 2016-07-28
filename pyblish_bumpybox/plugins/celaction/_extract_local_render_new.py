import os
import re
import _winreg
import subprocess

import pyblish.api


class ExtractImages(pyblish.api.InstancePlugin):

    label = "Images"
    families = ["img.local.*"]
    order = pyblish.api.ExtractorOrder

    def process(self, instance):

        progpath = instance.context.data["kwargs"]["data"]["progpath"][:-1]
        exe = os.path.join(progpath, "CelAction2D.exe")

        scene_file = instance.context.data["currentFile"]

        ext = os.path.splitext(instance.data["family"])[1]
        output_path = scene_file.replace(".scn", ext)

        # getting submission parameters
        start = instance.context.data["kwargs"]["data"]["start"]
        end = instance.context.data["kwargs"]["data"]["end"]
        width = instance.context.data["kwargs"]["data"]["x"]
        height = instance.context.data["kwargs"]["data"]["y"]

        # Modify registry for frame separation
        path = r"Software\CelAction\CelAction2D\User Settings"
        _winreg.CreateKey(_winreg.HKEY_CURRENT_USER, path)
        hKey = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, path, 0,
                               _winreg.KEY_ALL_ACCESS)

        _winreg.SetValueEx(hKey, "RenderNameUseSeparator", 0,
                           _winreg.REG_DWORD, 1)
        _winreg.SetValueEx(hKey, "RenderNameSeparator", 0, _winreg.REG_SZ, ".")

        # process render
        args = [exe, scene_file, "-a", "-s", start, "-e", end, "-x", width,
                "-y", height, "-d", os.path.dirname(output_path),
                "-r", os.path.basename(output_path),
                "-=", "AbsoluteFrameNumber=on", "-=", "PadDigits=4",
                "-=", "ClearAttachment=on"]

        self.log.info("Arguments to execute: %s" % args)
        subprocess.call(args)

        # process rendered images
        pattern = os.path.splitext(os.path.basename(output_path))[0]
        pattern += r"\.[0-9]{4}" + ext
        self.log.info("Pattern generated: \"{0}\"".format(pattern))

        files = []
        current_dir = os.path.dirname(output_path)
        for f in os.listdir(current_dir):
            if re.match(pattern, f):
                files.append(os.path.join(current_dir, f))

        path = os.path.splitext(output_path)[0] + ".%04d" + ext
        instance.data["outputPaths"] = {path: files}
        self.log.info("Files found: " + str(instance.data["outputPaths"]))


class ExtractRenderMovie(pyblish.api.InstancePlugin):

    label = "Movie"
    families = ["img.local.*"]
    order = ExtractImages.order + 0.1

    def frames_to_timecode(self, frames, framerate):

        h = str(int(frames / (3600 * framerate))).zfill(2)
        m = str(int(frames / (60 * framerate) % 60)).zfill(2)
        s = int(float(frames) / framerate % 60)
        f = float("0." + str((float(frames) / framerate) - s).split(".")[1])
        f = int(f / (1.0 / framerate))

        return "%s:%s:%s:%s" % (h, m, str(s).zfill(2), str(f).zfill(2))

    def process(self, instance):

        paths = []
        for path in instance.data["outputPaths"]:
            start = instance.context.data["kwargs"]["data"]["start"]
            args = ["ffmpeg.exe", "-gamma", "2.2", "-framerate", "25",
                    "-start_number", start, "-i", path]

            if ("audio" in instance.context.data and
               os.path.exists(instance.context.data["audio"])):
                args.extend(["-i", instance.context.data["audio"]])

            output_path = os.path.splitext(path.replace(".%04d", ""))[0]
            output_path = output_path + ".mov"
            vf = "scale=trunc(iw/2)*2:trunc(ih/2)*2,colormatrix=bt601:bt709"
            args.extend(["-q:v", "0", "-pix_fmt", "yuv420p", "-vf", vf,
                         "-timecode", self.frames_to_timecode(int(start), 25),
                         "-y", output_path])

            self.log.info("Arguments to execute: %s" % args)
            p = subprocess.Popen(args, stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            p.wait()
            msg = p.communicate()[1].replace("\n", "\n\n")
            assert p.returncode == 0, msg

            paths.append(output_path)

        for path in paths:
            instance.data["outputPaths"][path] = path
        """
        # publish to ftrack
        task = ftrack.Task(instance.context.data["ftrackData"]["Task"]["id"])
        asset = task.getParent().createAsset(task.getName(), "mov", task=task)

        version = None
        for v in asset.getVersions():
            if v.getVersion() == version_number:
                version = v

        if not version:
            version = asset.createVersion()
            version.set("version", version_number)

        version.publish()

        try:
            version.createComponent(name=str(instance), path=output_path)
        except:
            msg = "Ftrack component \"%s\" already exists" % str(instance)
            self.log.warning(msg)
        """
