import pyblish.api


class ExtractHieroFtrackShot(pyblish.api.InstancePlugin):
    """ Creates ftrack shots by the name of the shot. """

    order = pyblish.api.ExtractorOrder
    families = ["ftrack", "trackItem"]
    match = pyblish.api.Subset
    label = "Ftrack Shot"
    optional = True
    hosts = ["hiero"]

    def frames_to_timecode(self, frames, framerate):

        h = str(int(frames / (3600 * framerate))).zfill(2)
        m = str(int(frames / (60 * framerate) % 60)).zfill(2)
        s = int(float(frames) / framerate % 60)

        return "%s:%s:%s" % (h, m, str(s).zfill(2))

    def create_shot(self, parent, shot_name):
        import traceback

        import ftrack

        shot = None

        try:
            shot = parent.createShot(shot_name)

            msg = "Creating new shot with name \"{}{}\".".format(parent, shot_name)
            self.log.info(msg)
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

        return shot

    def get_shot(self, path):
        import ftrack

        path_str = "/".join(path)

        try:
            shot = ftrack.getShot(path)
            msg = "Found shot with id {} at path \"{}\".".format(shot.getId(), path_str)
            self.log.info(msg)

            return shot
        except:
            msg = "Didn't find shot with path \"{}\".".format(path_str)
            self.log.info(msg)

        return False

    def path_to_shot(self, parents, item):
        import traceback

        import ftrack

        path = []
        for p in parents:
            path.append(p.getName())
        path.reverse()

        # Setup parent.
        parent = parents[0]
        if "--" in item.name():
            name_split = item.name().split("--")

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

        return copy_path, parent

    def get_or_create_shot(self, instance):
        import ftrack

        ftrack_data = instance.context.data("ftrackData")
        task = ftrack.Task(ftrack_data["Task"]["id"])
        parents = task.getParents()
        item = instance[0]

        path, parent = self.path_to_shot(parents, item)

        shot_name = item.name()

        if "--" in shot_name:
            shot_name = shot_name.split("--")[-1]

        shot = self.get_shot(path + [shot_name])

        if not shot:
            shot = self.create_shot(parent, shot_name)

        return shot

    def process(self, instance):
        import ftrack

        item = instance[0]

        # Get/Create shot
        shot = None
        for tag in item.tags():
            if tag.name() == "ftrack":
                metadata = tag.metadata()

                if 'tag.id' in metadata:
                    shot = ftrack.Shot(metadata["tag.id"])
                else:
                    shot = self.get_or_create_shot(instance)

        instance.data["ftrackShotId"] = shot.getId()
        instance.data["ftrackShot"] = shot

        # Store shot id on tag
        for tag in item.tags():
            if tag.name() == "ftrack":
                tag.metadata().setValue("tag.id", shot.getId())

        # Assign attributes to shot.
        sequence = item.parent().parent()

        shot.set("fstart", value=1)
        shot.set("fps", value=sequence.framerate().toFloat())

        duration = item.sourceOut() - item.sourceIn()
        duration = abs(int(round((abs(duration) + 1) / item.playbackSpeed())))
        shot.set("fend", value=duration)

        try:
            fmt = sequence.format()
            shot.set("width", value=fmt.width())
            shot.set("height", value=fmt.height())
        except Exception as e:
            self.log.warning("Could not set the resolution: " + str(e))

        # Get handles.
        handles = 0
        if "handles" in instance.data["families"]:
            for tag in instance.data["tagsData"]:
                if "handles" == tag.get("tag.family", ""):
                    handles = int(tag["tag.value"])
        instance.data["handles"] = handles

        shot.set("handles", value=handles)
