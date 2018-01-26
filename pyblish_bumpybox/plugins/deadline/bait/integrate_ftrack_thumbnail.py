from pyblish import api


class IntegrateFtrackThumbnail(api.ContextPlugin):
    """ Integrates output """

    families = ["img.*", "mov.*"]
    order = api.IntegratorOrder

    def process(self, instance):
        import os
        import subprocess

        from Deadline import Scripting
        import ftrack

        # Get FFmpeg executable from Deadline plugin config
        config = Scripting.RepositoryUtils.GetPluginConfig("FFmpeg")
        executables = config.GetConfigEntry("FFmpeg_RenderExecutable")
        existing_executables = []
        for exe in executables.split(";"):
            if os.path.exists(exe):
                existing_executables.append(exe)

        msg = "No FFmpeg executable found in plugin configuration;"
        msg += "\n" + executables
        assert existing_executables, msg

        # Get random file from instance
        input_path = instance.data["files"].itervalues().next()[0]

        # Generate ffmpeg arguments and process
        input_args = []
        if "img.*" in instance.data["families"]:
            vf = "scale=-1:108"
            if os.path.splitext(input_path)[1] == ".exr":
                vf += ",lutrgb=r=gammaval(0.45454545):"
                vf += "g=gammaval(0.45454545):"
                vf += "b=gammaval(0.45454545)"
            input_args.extend(["-vf", vf])
        elif "mov.*" in instance.data["families"]:
            input_args.extend(["-vf", "thumbnail,scale=-1:108", "-frames:v",
                               "1"])

        output_path = os.path.splitext(input_path)[0]
        output_path += '_thumbnail.png'

        self.log.info("input path: " + input_path)
        self.log.info("output path: " + output_path)

        args = [existing_executables[0]]
        args.extend(['-i', input_path] + input_args + ['-y',
                    output_path])

        self.log.info("Args: %s" % args)
        subprocess.call(args)

        # Uploading thumbnail and clean up disk files.
        asset_version = instance.data('ftrackAssetVersion')
        version = ftrack.AssetVersion(asset_version['id'])
        version.createThumbnail(output_path)

        if os.path.exists(output_path):
            os.remove(output_path)
