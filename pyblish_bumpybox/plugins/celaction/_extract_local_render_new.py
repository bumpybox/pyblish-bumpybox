import os
import re
import _winreg
import subprocess
import tempfile

import pyblish.api


class ExtractImages(pyblish.api.InstancePlugin):

    label = "Images"
    families = ["img.local.*"]
    order = pyblish.api.ExtractorOrder

    def render_images(self, instance):

        progpath = instance.context.data["kwargs"]["data"]["progpath"][:-1]
        exe = os.path.join(progpath, "CelAction2D.exe")

        scene_file = instance.context.data["currentFile"]

        output_path = scene_file.replace(".scn", ".png")

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

        if instance.data["name"] == "levels":
            args.append("-l")

        self.log.info("Arguments to execute: %s" % args)
        subprocess.call(args)

        pattern = os.path.splitext(os.path.basename(output_path))[0]
        if instance.data["name"] == "levels":
            pattern += "_.+"
        pattern += r"\.[0-9]{4}\.png"
        self.log.info("Pattern generated: \"{0}\"".format(pattern))

        files = {}
        current_dir = os.path.dirname(output_path)
        for f in os.listdir(current_dir):
            m = re.match(pattern, f)
            if m:
                name = f[:-8] + "%04d.png"
                if name in files:
                    files[name].append(os.path.join(current_dir, f))
                else:
                    files[name] = [os.path.join(current_dir, f)]

        instance.data["outputPaths"] = files
        self.log.info("Files found: " + str(instance.data["outputPaths"]))

    def process(self, instance):

        # render images
        self.render_images(instance)


class ExtractMovie(pyblish.api.InstancePlugin):

    label = "Movie"
    families = ["mov.local.*"]
    order = ExtractImages.order + 0.1

    def frames_to_timecode(self, frames, framerate):

        h = str(int(frames / (3600 * framerate))).zfill(2)
        m = str(int(frames / (60 * framerate) % 60)).zfill(2)
        s = int(float(frames) / framerate % 60)
        f = float("0." + str((float(frames) / framerate) - s).split(".")[1])
        f = int(f / (1.0 / framerate))

        return "%s:%s:%s:%s" % (h, m, str(s).zfill(2), str(f).zfill(2))

    def process(self, instance):

        # checking whether the images are already rendered
        images_exists = True
        scene_file = instance.context.data["currentFile"]
        images_path = scene_file.replace(".scn", ".%04d.png")
        start = int(instance.context.data["kwargs"]["data"]["start"])
        end = int(instance.context.data["kwargs"]["data"]["end"])

        instance.data["outputPaths"] = {images_path: []}
        for frame in range(start, end + 1):
            f = images_path % frame
            if os.path.exists(f):
                instance.data["outputPaths"][images_path].append(f)
            else:
                images_exists = False

        # if the images aren't rendered, rerender the image batch
        if not images_exists:
            obj = ExtractImages()
            obj.render_images(instance)
            self.log.info("Not all images were found, rendering new ones.")

        # render movie
        args = ["ffmpeg.exe", "-gamma", "2.2", "-framerate", "25",
                "-start_number", str(start), "-i", images_path]

        if ("audio" in instance.context.data and
           os.path.exists(instance.context.data["audio"])):
            args.extend(["-i", instance.context.data["audio"]])

        movie_path = os.path.splitext(images_path.replace(".%04d", ""))[0]
        movie_path = movie_path + ".mov"
        vf = "scale=trunc(iw/2)*2:trunc(ih/2)*2,colormatrix=bt601:bt709"
        args.extend(["-q:v", "0", "-pix_fmt", "yuv420p", "-vf", vf,
                     "-timecode", self.frames_to_timecode(int(start), 25),
                     "-y", movie_path])
        self.log.info("Arguments to execute: %s" % args)

        temp = tempfile.TemporaryFile()
        return_code = subprocess.call(args, stdout=temp, stderr=temp,
                                      stdin=temp)
        temp.seek(0)
        output = temp.read()
        temp.close()

        # feedback any errors
        assert return_code == 0, output

        # cleanup images if generated sole for the movie
        if not images_exists:
            for frame in range(start, end + 1):
                f = images_path % frame
                if os.path.exists(f):
                    os.remove(f)
                    self.log.info("Removing source: \"%s\"" % f)

        # finishing attributes
        instance.data["outputPaths"] = {movie_path: movie_path}
