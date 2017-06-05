import os
import _winreg
import subprocess

import pyblish.api
import pyblish_standalone
import pipeline_schema
import ftrack


class ExtractCelactionRenderImages(pyblish.api.InstancePlugin):

    label = 'Render Images'
    families = ['render']
    order = pyblish.api.ExtractorOrder
    active = False
    optional = True

    def process(self, instance):

        progpath = instance.context.data['kwargs']['data']['progpath'][:-1]
        exe = os.path.join(progpath, 'CelAction2D.exe')

        path = os.path.dirname(pyblish_standalone.kwargs['path'][0])
        filename = os.path.basename(pyblish_standalone.kwargs['path'][0])
        scene_file = os.path.join(path, 'publish', filename).replace('\\', '/')

        # getting submission parameters
        start = instance.context.data['kwargs']['data']['start']
        end = instance.context.data['kwargs']['data']['end']
        width = instance.context.data['kwargs']['data']['x']
        height = instance.context.data['kwargs']['data']['y']

        # get version data
        version_number = 1
        if instance.context.has_data('version'):
            version_number = instance.context.data('version')

        # get output filename
        data = pipeline_schema.get_data()
        data['extension'] = 'png'
        data['output_type'] = 'img'
        data['name'] = instance.data["name"]
        data['version'] = version_number
        output_path = pipeline_schema.get_path('output_sequence', data)

        # Modify registry for frame separation
        path = r'Software\CelAction\CelAction2D\User Settings'
        _winreg.CreateKey(_winreg.HKEY_CURRENT_USER, path)
        hKey = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, path, 0,
                               _winreg.KEY_ALL_ACCESS)

        _winreg.SetValueEx(hKey, 'RenderNameUseSeparator', 0,
                           _winreg.REG_DWORD, 1)
        _winreg.SetValueEx(hKey, 'RenderNameSeparator', 0, _winreg.REG_SZ,
                           '.')

        # create output directory
        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))

        # process render
        args = [exe, scene_file, '-a', '-s', start, '-e', end, '-x', width,
                '-y', height, '-d', os.path.dirname(output_path),
                '-r', os.path.basename(output_path).replace('.%04d', ''),
                '-=', 'AbsoluteFrameNumber=on', '-=', 'PadDigits=4',
                '-=', 'ClearAttachment=on']

        self.log.info('Arguments to execute: %s' % args)
        subprocess.call(args)

        # publish to ftrack
        task = ftrack.Task(instance.context.data['ftrackData']['Task']['id'])
        asset = task.getParent().createAsset(task.getName(), 'img', task=task)

        version = None
        for v in asset.getVersions():
            if v.getVersion() == version_number:
                version = v

        if not version:
            version = asset.createVersion()
            version.set('version', version_number)

        version.publish()

        try:
            version.createComponent(name=instance.data["name"], path=output_path)
        except:
            msg = 'Ftrack component "%s" already exists' % instance.data["name"]
            self.log.warning(msg)


class ExtractCelactionRenderMovie(pyblish.api.InstancePlugin):

    label = 'Render Movie'
    families = ['render']
    order = ExtractCelactionRenderImages.order + 0.1
    active = False
    optional = True

    def frames_to_timecode(self, frames, framerate):

        h = str(int(frames / (3600 * framerate))).zfill(2)
        m = str(int(frames / (60 * framerate) % 60)).zfill(2)
        s = int(float(frames) / framerate % 60)
        f = float('0.' + str((float(frames) / framerate) - s).split('.')[1])
        f = int(f / (1.0 / framerate))

        return '%s:%s:%s:%s' % (h, m, str(s).zfill(2), str(f).zfill(2))

    def process(self, instance):

        exe = 'ffmpeg.exe'

        # getting submission parameters
        start = instance.context.data['kwargs']['data']['start']

        # get version data
        version_number = 1
        if instance.context.has_data('version'):
            version_number = instance.context.data('version')

        # get input images
        data = pipeline_schema.get_data()
        data['extension'] = 'png'
        data['output_type'] = 'img'
        data['name'] = instance.data["name"]
        data['version'] = version_number
        image_files = pipeline_schema.get_path('output_sequence', data)

        # get output file
        data = pipeline_schema.get_data()
        data['version'] = version_number
        data['extension'] = 'mov'
        data['output_type'] = 'mov'
        data['name'] = instance.data["name"]
        output_path = pipeline_schema.get_path('output_file', data)

        # get audio file
        task = ftrack.Task(instance.context.data['ftrackData']['Task']['id'])
        audio_file = ''
        try:
            asset = task.getParent().getAsset('audio', 'audio')
            component = asset.getVersions()[-1].getComponent()
            audio_file = component.getFilesystemPath()
        except:
            self.log.warning("Couldn't find any audio file on Ftrack.")

        # create output directory
        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))

        # process render
        args = [exe, '-gamma', '2.2', '-framerate', '25',
                '-start_number', start, '-i', image_files]

        if os.path.exists(audio_file):
            args.extend(['-i', audio_file])

        vf = 'scale=trunc(iw/2)*2:trunc(ih/2)*2,colormatrix=bt601:bt709'
        args.extend(['-q:v', '0', '-pix_fmt', 'yuv420p', '-vf', vf,
                     '-timecode', self.frames_to_timecode(int(start), 25),
                     '-y', output_path])

        self.log.info('Arguments to execute: %s' % args)
        subprocess.call(args)

        # publish to ftrack
        task = ftrack.Task(instance.context.data['ftrackData']['Task']['id'])
        asset = task.getParent().createAsset(task.getName(), 'mov', task=task)

        version = None
        for v in asset.getVersions():
            if v.getVersion() == version_number:
                version = v

        if not version:
            version = asset.createVersion()
            version.set('version', version_number)

        version.publish()

        try:
            version.createComponent(name=instance.data["name"], path=output_path)
        except:
            msg = 'Ftrack component "%s" already exists' % instance.data["name"]
            self.log.warning(msg)
