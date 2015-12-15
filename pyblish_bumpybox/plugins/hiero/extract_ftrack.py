import os
import inspect
import subprocess
import tempfile
import traceback

import pyblish.api
import ftrack


class ExtractFtrackShots(pyblish.api.Extractor):
    """ Creates ftrack shots by the name of the shot
    """

    families = ['ftrack', 'nuke']
    label = 'Ftrack Shots'
    optional = True

    def get_path(self, shot, context):

        ftrack_data = context.data('ftrackData')

        path = [ftrack_data['Project']['root']]
        path.append('renders')
        path.append('audio')
        for p in reversed(shot.getParents()[:-1]):
            path.append(p.getName())

        path.append(shot.getName())

        # get version data
        version = 1
        if context.has_data('version'):
            version = context.data('version')
        version_string = 'v%s' % str(version).zfill(3)

        filename = [shot.getName(), version_string, 'wav']
        path.append('.'.join(filename))

        return os.path.join(*path).replace('\\', '/')

    def frames_to_timecode(self, frames, framerate):

        h = str(int(frames / (3600 * framerate))).zfill(2)
        m = str(int(frames / (60 * framerate) % 60)).zfill(2)
        s = int(float(frames) / framerate % 60)
        f = float('0.' + str((float(frames) / framerate) - s).split('.')[1])
        f = int(f / (1.0 / framerate))

        return '%s:%s:%s' % (h, m, str(s).zfill(2))

    def process(self, instance, context):

        # skipping if not launched from ftrack
        if not context.has_data('ftrackData'):
            return

        ftrack_data = context.data('ftrackData')
        task = ftrack.Task(ftrack_data['Task']['id'])
        parents = task.getParents()
        item = instance[0]

        path = []
        for p in parents:
            path.append(p.getName())

        # setup parent
        parent = parents[0]
        if '--' in item.name():
            name_split = item.name().split('--')
            if len(name_split) == 2:
                try:
                    copy_path = list(path)
                    copy_path.append(name_split[0])
                    parent = ftrack.getSequence(copy_path)
                except:
                    parent = parents[0].createSequence(name_split[0])
            if len(name_split) == 3:
                try:
                    copy_path = list(path)
                    copy_path.append(name_split[0])
                    parent = ftrack.getSequence(copy_path)
                except:
                    parent = parents[0].createEpisode(name_split[0])

                parents = [parent] + parents

                try:
                    copy_path.append(name_split[1])
                    parent = ftrack.getSequence(copy_path)
                except:
                    parent = parents[0].createSequence(name_split[1])

        # creating shot
        shot_name = item.name()
        duration = item.sourceOut() - item.sourceIn()
        duration = abs(int(round((abs(duration) + 1) / item.playbackSpeed())))

        if '--' in item.name():
            shot_name = item.name().split('--')[-1]

        try:
            shot = parent.createShot(shot_name)

            shot.set('fstart', value=1)
            shot.set('fend', value=duration)

            path = self.get_path(shot, context)

            instance.set_data('ftrackId', value=shot.getId())

            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))

            item.sequence().writeAudioToFile(path, item.timelineIn(),
                                             item.timelineOut())

            msg = 'Creating new shot with name'
            msg += ' "%s"' % item.name()
            self.log.info(msg)

            instance.data['ftrackShot'] = shot
        except:
            path = []
            try:
                for p in reversed(parent.getParents()):
                    path.append(p.getName())
            except:
                pass
            path.append(parent.getName())
            path.append(shot_name)
            shot = ftrack.getShot(path)

            instance.set_data('ftrackId', value=shot.getId())

            shot.set('fstart', value=1)
            shot.set('fend', value=duration)

            path = self.get_path(shot, context)

            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))

            item.sequence().writeAudioToFile(path, item.timelineIn(),
                                             item.timelineOut())

            instance.data['ftrackShot'] = shot

        d = os.path.dirname
        tools_path = d(d(d(d(d(d(inspect.getfile(inspect.currentframe())))))))
        exe = os.path.join(tools_path, 'ffmpeg', 'bin', 'ffmpeg.exe')
        input_path = item.source().mediaSource().fileinfos()[0].filename()
        ext = os.path.splitext(input_path)[1]
        output_path = os.path.splitext(input_path)[0]
        output_path += '_thumbnail.png'
        output_path = os.path.join(tempfile.gettempdir(),
                                   os.path.basename(output_path))
        input_cmd = ''
        fps = item.sequence().framerate().toFloat()

        if ext == '.mov':
            arg = ' scale=-1:108'
            input_cmd = ' -vf' + arg + ' -vframes' + ' 1'
        else:
            arg = ' scale=-1:108'
            if os.path.splitext(input_path)[1] == '.exr':
                arg += ',lutrgb=r=gammaval(0.45454545):'
                arg += 'g=gammaval(0.45454545):'
                arg += 'b=gammaval(0.45454545)'
            input_cmd = ' -vf' + arg

        tc = self.frames_to_timecode(item.sourceIn(), fps)
        cmd = exe + ' -ss ' + tc + ' -i "' + input_path + '" ' + input_cmd
        cmd += ' -y "' + output_path + '"'
        subprocess.call(cmd)

        # creating thumbnails
        thumb = shot.createThumbnail(output_path)
        for t in shot.getTasks():
            t.set('thumbid', value=thumb.get('entityId'))

        if os.path.exists(output_path):
            os.remove(output_path)


class ExtractFtrackTasks(pyblish.api.Extractor):
    """
    """

    families = ['task']
    label = 'Ftrack Tasks'
    optional = True
    order = ExtractFtrackShots.order + 0.1

    def getTaskTypeByName(self, name):
        for t in ftrack.getTaskTypes():
            if t.getName().lower() == name.lower():
                return t

        return None

    def process(self, instance):

        for t in instance.data['taskTypes']:
            task_type = self.getTaskTypeByName(t)
            try:
                shot = instance.data['ftrackShot']
                shot.createTask(task_type.getName().lower(),
                                taskType=task_type)
            except:
                self.log.error(traceback.format_exc())
