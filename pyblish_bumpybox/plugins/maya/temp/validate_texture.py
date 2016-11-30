import os
import shutil

import pyblish.api
from pyblish_bumpybox.plugins.maya import utils


class RepairTexture(pyblish.api.Action):

    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):

        # Get the errored instances
        failed = []
        for result in context.data["results"]:
            if (result["error"] is not None and result["instance"] is not None
               and result["instance"] not in failed):
                failed.append(result["instance"])

        # Apply pyblish.logic to get the instances for the plug-in
        instances = pyblish.api.instances_by_plugin(failed, plugin)

        for instance in instances:

            node = instance[0]
            src = node.fileTextureName.get()
            dst = utils.texture_path(instance)

            if not os.path.exists(os.path.dirname(dst)):
                os.makedirs(os.path.dirname(dst))

            shutil.copy(src, dst)

            node.fileTextureName.set(dst)


class ValidateTexture(pyblish.api.Validator):
    """
    """

    families = ['texture']
    label = 'Texture'
    actions = [RepairTexture]

    def process(self, instance, context):

        node = instance[0]
        src = node.fileTextureName.get()
        dst = utils.texture_path(instance)

        msg = 'Current path: %s\n\nExpected path: %s' % (src, dst)
        assert src == dst, msg
