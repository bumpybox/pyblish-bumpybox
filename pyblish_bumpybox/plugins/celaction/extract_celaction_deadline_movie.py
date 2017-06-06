import pyblish.api
import pipeline_schema


class ExtractCelactionDeadlineMovie(pyblish.api.InstancePlugin):

    hosts = ["celaction"]
    label = "Movie"
    families = ["*"]
    order = pyblish.api.ExtractorOrder + 0.4

    def frames_to_timecode(self, frames, framerate):

        h = str(int(frames / (3600 * framerate))).zfill(2)
        m = str(int(frames / (60 * framerate) % 60)).zfill(2)
        s = int(float(frames) / framerate % 60)
        f = float("0." + str((float(frames) / framerate) - s).split(".")[1])
        f = int(f / (1.0 / framerate))

        return "%s:%s:%s:%s" % (h, m, str(s).zfill(2), str(f).zfill(2))

    def process(self, instance):

        # skipping instance if data is missing
        if "deadlineData" not in instance.data:
            msg = "No deadlineData present. Skipping \"%s\"" % instance
            self.log.info(msg)
            return

        # skipping instance if the required data is missing
        if "movie" not in instance.data:
            msg = "Missing movie data."
            self.log.info(msg)
            return

        # setting ffmpeg settings
        extra_info_key_value = {}
        job_data = instance.data["deadlineData"]["job"]
        fps = instance.data["movie"]["fps"]
        first_frame = instance.data["movie"]["first_frame"]
        audio = instance.data["movie"]["audio"]

        if "ExtraInfoKeyValue" in job_data:
            extra_info_key_value = job_data["ExtraInfoKeyValue"]

        args = "-q:v 0 -pix_fmt yuv420p -vf scale=trunc(iw/2)*2:trunc(ih/2)*2"
        args += ",colormatrix=bt601:bt709"
        args += " -timecode %s" % self.frames_to_timecode(first_frame, fps)
        extra_info_key_value["FFMPEGOutputArgs0"] = args

        args = "-gamma 2.2 -framerate %s -start_number %s" % (fps, first_frame)
        extra_info_key_value["FFMPEGInputArgs0"] = args

        input_file = job_data["OutputFilename0"].replace("####", "%04d")
        args = input_file
        if audio:
            args += " -i " + audio.replace("\\", "/")
        extra_info_key_value["FFMPEGInput0"] = args

        # get version data
        version = 1
        if instance.context.has_data("version"):
            version = instance.context.data("version")

        # expected path
        data = pipeline_schema.get_data()
        data["version"] = version
        data["extension"] = "mov"
        data["output_type"] = "mov"
        data["name"] = instance.data["name"]
        output_file = pipeline_schema.get_path("output_file", data)

        extra_info_key_value["FFMPEGOutput0"] = output_file

        job_data["ExtraInfoKeyValue"] = extra_info_key_value
