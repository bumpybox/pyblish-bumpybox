from pyblish import api
from pyblish_bumpybox import inventory


class RepairNukeSettings(api.Action):

    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):
        import nuke
        import ftrack

        ftrack_data = context.data("ftrackData")
        task = ftrack.Task(ftrack_data["Task"]["id"])
        parent = task.getParent()

        nuke.root()["fps"].setValue(parent.get("fps"))

        handles = parent.get("handles")
        nuke.root()["first_frame"].setValue(parent.getFrameStart() - handles)
        nuke.root()["last_frame"].setValue(parent.getFrameEnd() + handles)


class ValidateNukeSettings(api.ContextPlugin):
    """ Validates nuke settings. """

    order = inventory.get_order(__file__, "ValidateNukeSettings")
    families = ["scene"]
    optional = True
    label = "Settings"
    actions = [RepairNukeSettings]
    hosts = ["nuke"]

    def process(self, context):
        import nuke
        import ftrack

        ftrack_data = context.data("ftrackData")

        task = ftrack.Task(ftrack_data["Task"]["id"])
        parent = task.getParent()

        # skipping all non shot related tasks
        if parent.get("entityType") == "show":
            return
        if parent.getObjectType() != "Shot":
            return

        handles = parent.get("handles")

        # validating fps
        local_fps = nuke.root()["fps"].value()

        online_fps = parent.get("fps")

        msg = "FPS is incorrect."
        msg += "\n\nLocal fps: %s" % local_fps
        msg += "\n\nOnline fps: %s" % online_fps
        assert local_fps == online_fps, msg

        # validating first frame
        local_first_frame = nuke.root()["first_frame"].value()

        online_first_frame = parent.getFrameStart() - handles

        msg = "First frame is incorrect."
        msg += "\n\nLocal last frame: %s" % local_first_frame
        msg += "\n\nOnline last frame: %s" % online_first_frame
        assert local_first_frame == online_first_frame, msg

        # validating last frame
        local_last_frame = nuke.root()["last_frame"].value()

        online_last_frame = parent.getFrameEnd() + handles

        msg = "Last frame is incorrect."
        msg += "\n\nLocal last frame: %s" % local_last_frame
        msg += "\n\nOnline last frame: %s" % online_last_frame
        assert local_last_frame == online_last_frame, msg
