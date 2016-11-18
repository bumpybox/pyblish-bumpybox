import os
import tempfile
import traceback
import time
import shutil

import pyblish.api
import ftrack
import hiero
import pipeline_schema


class ExtractFtrackShots(pyblish.api.Extractor):
    """ Creates ftrack shots by the name of the shot
    """

    families = ['ftrack', 'nuke', 'task']
    label = 'Ftrack Shots'
    optional = True

    def frames_to_timecode(self, frames, framerate):

        h = str(int(frames / (3600 * framerate))).zfill(2)
        m = str(int(frames / (60 * framerate) % 60)).zfill(2)
        s = int(float(frames) / framerate % 60)
        f = float('0.' + str((float(frames) / framerate) - s).split('.')[1])
        f = int(f / (1.0 / framerate))

        return '%s:%s:%s' % (h, m, str(s).zfill(2))

    def process(self, instance):

        context = instance.context

        # skipping if not launched from ftrack
        if not context.has_data('ftrackData'):
            return

        # get version data
        version = 1
        if context.has_data('version'):
            version = context.data('version')

        ftrack_data = context.data('ftrackData')
        task = ftrack.Task(ftrack_data['Task']['id'])
        parents = task.getParents()
        item = instance[0]

        path = []
        for p in parents:
            path.append(p.getName())
        path.reverse()

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
                    self.log.error(traceback.format_exc())
                    parent = parents[0].createSequence(name_split[0])
            if len(name_split) == 3:
                try:
                    copy_path = list(path)
                    copy_path.append(name_split[0])
                    parent = ftrack.getSequence(copy_path)
                except:
                    self.log.error(traceback.format_exc())
                    parent = parents[0].createEpisode(name_split[0])

                parents = [parent] + parents

                try:
                    copy_path.append(name_split[1])
                    parent = ftrack.getSequence(copy_path)
                except:
                    self.log.error(traceback.format_exc())
                    parent = parents[0].createSequence(name_split[1])

        # creating shot
        shot_name = item.name()
        duration = item.sourceOut() - item.sourceIn()
        duration = abs(int(round((abs(duration) + 1) / item.playbackSpeed())))

        if '--' in item.name():
            shot_name = item.name().split('--')[-1]

        shot = None
        try:
            shot = parent.createShot(shot_name)

            msg = 'Creating new shot with name'
            msg += ' "%s"' % item.name()
            self.log.info(msg)

            instance.data['ftrackId'] = shot.getId()
            instance.data['ftrackShot'] = shot
        except:
            self.log.error(traceback.format_exc())

            path = []
            try:
                for p in reversed(parent.getParents()):
                    path.append(p.getName())
            except:
                pass
            path.append(parent.getName())
            path.append(shot_name)
            shot = ftrack.getShot(path)

            instance.data['ftrackId'] = shot.getId()
            instance.data['ftrackShot'] = shot

        # publishing audio
        if 'audio' in instance.data:
            asset = shot.createAsset(name='audio', assetType='audio')

            assetversion = None
            for v in asset.getVersions():
                if v.getVersion() == version:
                    assetversion = v

            if not assetversion:
                assetversion = asset.createVersion(taskid=shot.getId())
                assetversion.publish()
                assetversion.set('version', value=int(version))

            # get output path
            data = pipeline_schema.get_data()
            data['version'] = version
            data['extension'] = 'wav'
            data['output_type'] = 'audio'
            data['name'] = instance.data["name"]
            output_file = pipeline_schema.get_path('output_file', data)
            self.log.info(output_file)

            # copy audio file
            output_dir = os.path.dirname(output_file)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            shutil.copy(instance.data['audio'], output_file)

            try:
                assetversion.createComponent(path=output_file)
            except:
                self.log.error(traceback.format_exc())

        # assign attributes to shot
        shot.set('fstart', value=1)
        shot.set('fend', value=duration)
        shot.set('handles', value=instance.data['handles'])

        # generate_thumbnail
        try:
            self.generate_thumbnail(instance, item, shot)
        except:
            self.log.error(traceback.format_exc())

    def generate_thumbnail(self, instance, item, shot):
        nukeWriter = hiero.core.nuke.ScriptWriter()

        # getting top most track with media
        seq = item.parent().parent()
        item = seq.trackItemAt(item.timelineIn())

        root_node = hiero.core.nuke.RootNode(1, 1, fps=seq.framerate())
        nukeWriter.addNode(root_node)

        handles = instance.data['handles']

        item.addToNukeScript(script=nukeWriter, firstFrame=1,
                             includeRetimes=True, retimeMethod='Frame',
                             startHandle=handles, endHandle=handles)

        input_path = item.source().mediaSource().fileinfos()[0].filename()
        output_path = os.path.splitext(input_path)[0]
        output_path += '_thumbnail.png'
        output_path = os.path.join(tempfile.gettempdir(),
                                   os.path.basename(output_path))

        fmt = hiero.core.Format(300, 200, 1, 'thumbnail')
        fmt.addToNukeScript(script=nukeWriter)

        write_node = hiero.core.nuke.WriteNode(output_path)
        write_node.setKnob('file_type', 'png')
        nukeWriter.addNode(write_node)

        script_path = output_path.replace('.png', '.nk')
        nukeWriter.writeToDisk(script_path)
        self.log.info(script_path)
        logFileName = output_path.replace('.png', '.log')
        process = hiero.core.nuke.executeNukeScript(script_path,
                                                    open(logFileName, 'w'))

        while process.poll() is None:
            time.sleep(0.5)

        if os.path.exists(output_path):
            self.log.info("Thumbnail rendered successfully!")

            # creating thumbnails
            thumb = shot.createThumbnail(output_path)
            for t in shot.getTasks():
                t.set('thumbid', value=thumb.get('entityId'))
        else:
            self.log.error("Thumbnail failed to render")


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
                shot.createTask(t.lower(), taskType=task_type)
            except:
                self.log.error(traceback.format_exc())
